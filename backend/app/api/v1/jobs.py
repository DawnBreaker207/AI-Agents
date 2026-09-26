import logging
import os
import re as _re
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.models.job_watch import JobWatch

router = APIRouter(tags=["jobs"])
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_search_terms(keyword: str, level: Optional[str]) -> str:
    terms = []
    if level and level not in ("Tất cả", ""):
        terms.append(level)
    if keyword and keyword.strip():
        terms.append(keyword.strip())
    return " ".join(terms) if terms else "IT"


async def _expand_queries(keyword: str, db: AsyncSession) -> List[str]:
    """4.2 — mở rộng keyword bằng role_alias (tối đa 2 variant để tránh spam query)."""
    from app.models.category import RoleAlias
    kw = (keyword or "").strip()
    if not kw:
        return ["IT"]
    try:
        result = await db.execute(
            select(RoleAlias).where(RoleAlias.is_active == True).limit(50)
        )
        rows = result.scalars().all()
    except Exception:
        return [kw]
    variants = [kw]
    for row in rows:
        canon, alias = str(row.canonical_role or ""), str(row.alias or "")
        if canon.lower() == kw.lower() and alias and alias not in variants:
            variants.append(alias)
        elif alias.lower() == kw.lower() and canon and canon not in variants:
            variants.append(canon)
        if len(variants) >= 2:
            break
    return variants


_LEVEL_WORDS: dict[str, list[str]] = {
    "intern": ["intern", "thực tập", "thuc tap"],
    "junior": ["junior", "fresher", "entry"],
    "middle": ["middle", "mid-level", "mid level"],
    "senior": ["senior"],
    "lead": ["lead", "principal", "staff engineer", "architect", "manager"],
}
_LEVEL_MIN_YEARS: dict[str, int] = {"intern": 0, "junior": 0, "middle": 2, "senior": 3, "lead": 5}
_LEVEL_MAX_YEARS: dict[str, int] = {"intern": 1, "junior": 3, "middle": 5, "senior": 99, "lead": 99}
_YEARS_PATTERN = _re.compile(r"(\d+)\s*\+\s*(năm|years?|yrs?)|(\d+)\s*(năm|years?|yrs?)")


def _normalize_level(level: Optional[str]) -> Optional[str]:
    if not level or level in ("Tất cả", ""):
        return None
    low = level.lower()
    for key, words in _LEVEL_WORDS.items():
        if key in low or any(w in low for w in words):
            return key
    return None


def _post_filter_level(jobs: List[dict], level: Optional[str]) -> List[dict]:
    """4.2 — loại job ghi rõ cấp bậc khác với level yêu cầu; job không ghi level thì giữ."""
    want = _normalize_level(level)
    if not want:
        return jobs
    kept = []
    for job in jobs:
        text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        mentioned = {k for k, words in _LEVEL_WORDS.items()
                     if any(w in text for w in words)}
        if mentioned and want not in mentioned:
            continue  # ghi rõ level khác → loại
        years = [int(n) for tup in _YEARS_PATTERN.findall(text) for n in tup[:1] + tup[2:3] if n.isdigit()]
        if years:
            top = max(years)
            if not (_LEVEL_MIN_YEARS[want] <= top <= _LEVEL_MAX_YEARS[want]):
                continue
        kept.append(job)
    return kept


def _strip_html(text: str, limit: int = 300) -> str:
    import re
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:limit] + ("..." if len(clean) > limit else "")


def _make_job(*, id: str, title: str, company: str, location: str,
              location_type: str, work_model: str, url: str, source: str,
              description: str, posted_at, salary: str, tags: list) -> dict:
    return {
        "id": id, "title": title, "company": company, "location": location,
        "location_type": location_type, "work_model": work_model,
        "url": url, "source": source, "description": description,
        "posted_at": posted_at, "salary": salary, "tags": tags,
    }


# ── Overseas sources ─────────────────────────────────────────────────────────

async def _fetch_remotive(client: httpx.AsyncClient, q: str) -> List[dict]:
    """Remotive — curated remote tech jobs, free API."""
    print(f"[Remotive] Fetching q='{q}'", flush=True)
    try:
        r = await client.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": q, "limit": 20},
            timeout=12,
        )
        if r.status_code != 200:
            print(f"[Remotive] HTTP {r.status_code}", flush=True)
            return []
        jobs = r.json().get("jobs", [])
        print(f"[Remotive] Got {len(jobs)} jobs", flush=True)
        return [
            _make_job(
                id=f"remotive-{j['id']}",
                title=j.get("title", ""),
                company=j.get("company_name", ""),
                location=j.get("candidate_required_location") or "Worldwide",
                location_type="overseas", work_model="remote",
                url=j.get("url", ""), source="Remotive",
                description=_strip_html(j.get("description", "")),
                posted_at=j.get("publication_date"),
                salary=j.get("salary") or "",
                tags=j.get("tags") or [],
            )
            for j in jobs
        ]
    except Exception as e:
        print(f"[Remotive] ERR: {e}", flush=True)
        return []


async def _fetch_arbeitnow(client: httpx.AsyncClient, q: str) -> List[dict]:
    """Arbeitnow — visa-sponsored EU remote jobs, free API."""
    print(f"[Arbeitnow] Fetching q='{q}'", flush=True)
    try:
        r = await client.get(
            "https://www.arbeitnow.com/api/job-board-api",
            params={"search": q},
            timeout=12,
        )
        if r.status_code != 200:
            print(f"[Arbeitnow] HTTP {r.status_code}", flush=True)
            return []
        jobs = r.json().get("data", [])[:15]
        print(f"[Arbeitnow] Got {len(jobs)} jobs", flush=True)
        return [
            _make_job(
                id=f"arbeitnow-{j.get('slug', idx)}",
                title=j.get("title", ""),
                company=j.get("company_name", ""),
                location=j.get("location") or "EU / Remote",
                location_type="overseas", work_model="remote",
                url=j.get("url", ""), source="Arbeitnow",
                description=_strip_html(j.get("description", "")),
                posted_at=None, salary="",
                tags=j.get("tags") or [],
            )
            for idx, j in enumerate(jobs)
        ]
    except Exception as e:
        print(f"[Arbeitnow] ERR: {e}", flush=True)
        return []


async def _fetch_jobicy(client: httpx.AsyncClient, q: str) -> List[dict]:
    """Jobicy — global remote jobs, free public API (no key required)."""
    print(f"[Jobicy] Fetching q='{q}'", flush=True)
    try:
        r = await client.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"tag": q, "count": 15},
            timeout=12,
        )
        if r.status_code != 200:
            print(f"[Jobicy] HTTP {r.status_code}", flush=True)
            return []
        jobs = r.json().get("jobs", [])
        print(f"[Jobicy] Got {len(jobs)} jobs", flush=True)
        return [
            _make_job(
                id=f"jobicy-{j.get('id', idx)}",
                title=j.get("jobTitle", ""),
                company=j.get("companyName", ""),
                location=j.get("jobGeo") or "Worldwide",
                location_type="overseas", work_model="remote",
                url=j.get("url", ""), source="Jobicy",
                description=_strip_html(j.get("jobExcerpt", "")),
                posted_at=j.get("pubDate"),
                salary=j.get("annualSalaryMin", ""),
                tags=j.get("jobIndustry") or [],
            )
            for idx, j in enumerate(jobs)
        ]
    except Exception as e:
        print(f"[Jobicy] ERR: {e}", flush=True)
        return []


async def _fetch_themuse(client: httpx.AsyncClient, q: str) -> List[dict]:
    """The Muse — US/global tech jobs, free public API (no key required)."""
    print(f"[The Muse] Fetching q='{q}'", flush=True)
    try:
        # Không gửi param `level`: lọc cấp bậc ở tầng post-filter (4.2),
        # tránh hardcode "Entry Level" bất kể user chọn gì.
        r = await client.get(
            "https://www.themuse.com/api/public/jobs",
            params={"category": "Engineering", "page": 0},
            timeout=12,
        )
        if r.status_code != 200:
            print(f"[The Muse] HTTP {r.status_code}", flush=True)
            return []
        jobs = r.json().get("results", [])
        # Filter by keyword relevance in title/tags
        kw_lower = q.lower()
        jobs = [j for j in jobs if kw_lower in (j.get("name", "") + " ".join(
            t.get("name", "") for t in j.get("tags", [])
        )).lower()][:12]
        print(f"[The Muse] Got {len(jobs)} relevant jobs", flush=True)
        return [
            _make_job(
                id=f"muse-{j.get('id', idx)}",
                title=j.get("name", ""),
                company=(j.get("company") or {}).get("name", ""),
                location=", ".join(
                    loc.get("name", "") for loc in j.get("locations", [])
                ) or "US / Remote",
                location_type="overseas", work_model="hybrid",
                url=j.get("refs", {}).get("landing_page", ""), source="The Muse",
                description=_strip_html(j.get("contents", "")),
                posted_at=j.get("publication_date"),
                salary="",
                tags=[t.get("name", "") for t in j.get("tags", [])],
            )
            for idx, j in enumerate(jobs)
        ]
    except Exception as e:
        print(f"[The Muse] ERR: {e}", flush=True)
        return []







# ── Domestic: per-site DDGS search + strict URL validation ───────────────────

DOMESTIC_SITES = [
    ("itviec.com",       "ITviec"),
    ("topcv.vn",         "TopCV"),
    ("vietnamworks.com", "VietnamWorks"),
    ("careerviet.vn",    "CareerViet"),
    ("jobsgo.vn",        "JobsGo"),
    ("topdev.vn",        "TopDev"),
    ("glints.com",       "Glints"),
    ("hirex.vn",         "Hirex"),
    ("mywork.com.vn",    "MyWork"),
    ("timviecnhanh.com", "TimViecNhanh"),
]

# Per-site search config: (domain, display_label, max_raw_results)
# Sites with higher IT job density get higher limits
_SITE_CONFIGS: List[tuple] = [
    ("itviec.com",       "ITviec",        20),
    ("topcv.vn",         "TopCV",         20),
    ("topdev.vn",        "TopDev",        15),
    ("vietnamworks.com", "VietnamWorks",  15),
    ("careerviet.vn",    "CareerViet",    15),
    ("glints.com",       "Glints",        12),
    ("jobsgo.vn",        "JobsGo",        12),
    ("hirex.vn",         "Hirex",         10),
    ("mywork.com.vn",    "MyWork",        10),
    ("timviecnhanh.com", "TimViecNhanh",  10),
]


def _is_job_detail_url(url: str) -> bool:
    """Returns True only for individual job detail pages.
    Rejects homepages, category/search listings, blog posts, and CV templates.
    """
    u = url.lower().rstrip("/")

    if "itviec.com" in u:
        return "/it-jobs/" in u

    if "topcv.vn" in u:
        return "/tuyen-dung/" in u

    if "topdev.vn" in u:
        # TopDev job detail: /jobs/<slug> with numeric id embedded
        return "/jobs/" in u and not u.endswith("/jobs")

    if "vietnamworks.com" in u:
        return "/job/" in u or u.endswith("-jv") or (
            "/tuyen-dung/" in u and not u.endswith("/tuyen-dung")
        )

    if "jobsgo.vn" in u:
        # Job detail: /viec-lam/<slug>-<ID>.html where ID >= 5 digits
        if "/viec-lam/" in u and u.endswith(".html"):
            return bool(_re.search(r"-\d{5,}\.html$", u))
        return False

    if "careerviet.vn" in u or "careerbuilder.vn" in u:
        # Detail: /vi/tim-viec-lam/<slug>.<8-char-hex>.html
        if "/vi/tim-viec-lam/" in u and u.endswith(".html"):
            bad = ("-trang-", "/trang-", "/page-", "/tat-ca-viec-lam", "?page=")
            return not any(k in u for k in bad)
        return False

    if "glints.com" in u:
        # Glints job detail: /opportunities/<job-slug>
        return "/opportunities/" in u and not u.endswith("/opportunities")

    if "hirex.vn" in u:
        return "/viec-lam/" in u or "/job/" in u

    if "mywork.com.vn" in u:
        return "/tuyen-dung/" in u

    if "timviecnhanh.com" in u:
        return "/tuyen-dung/" in u

    return False


def _detect_source(url: str) -> str:
    for domain, label in DOMESTIC_SITES:
        if domain in url:
            return label
    return "Khác"


# Thành phố VN thường gặp trong tin tuyển dụng (regex, không dấu/có dấu)
_CITY_PATTERNS: list[tuple[str, str]] = [
    ("Hà Nội", r"hà\s*nội|ha\s*noi|hanoi"),
    ("TP. Hồ Chí Minh", r"hồ\s*chí\s*minh|ho\s*chi\s*minh|tp\.?\s*hcm|sài\s*gòn|sai\s*gon|quận\s*[0-9]|thủ\s*đức|thu\s*duc"),
    ("Đà Nẵng", r"đà\s*nẵng|da\s*nang|danang"),
    ("Hải Phòng", r"hải\s*phòng|hai\s*phong|haiphong"),
    ("Cần Thơ", r"cần\s*thơ|can\s*tho|cantho"),
    ("Huế", r"huế|hue(?!s)"),
    ("Nha Trang", r"nha\s*trang"),
    ("Bình Dương", r"bình\s*dương|binh\s*duong"),
    ("Đồng Nai", r"đồng\s*nai|dong\s*nai"),
    ("Vũng Tàu", r"vũng\s*tàu|vung\s*tau"),
    ("Hải Dương", r"hải\s*dương|hai\s*duong"),
    ("Bắc Ninh", r"bắc\s*ninh|bac\s*ninh"),
    ("Nghệ An", r"nghệ\s*an|nghe\s*an|vinh\b"),
    ("Remote", r"remote|làm\s*việc\s*từ\s*xa|work\s*from\s*home|wfh"),
]


def _extract_location(snippet: str) -> str:
    """Trích địa điểm thật từ snippet DDGS — không echo city_term (4.3)."""
    lowered = (snippet or "").lower()
    for label, pattern in _CITY_PATTERNS:
        if _re.search(pattern, lowered):
            return label
    return "Chưa xác định"


def _clean_title(title: str) -> str:
    for _, label in DOMESTIC_SITES:
        title = title.replace(f" - {label}", "").replace(f" | {label}", "")
    return title.strip()


def _parse_job_title_and_company(raw_title: str) -> tuple:
    """Extract job title and company name from a raw DuckDuckGo result title."""
    title = _clean_title(raw_title)
    company = ""

    # Strip "Tuyển dụng" prefix
    for prefix in ("tuyển dụng ", "tuyển ", "tuyen dung ", "hiring "):
        if title.lower().startswith(prefix):
            title = title[len(prefix):]
            break

    # Split on common company separators
    for sep in (" tại ", " at ", " - Công ty ", " @ "):
        if sep.lower() in title.lower():
            idx = title.lower().find(sep.lower())
            company = title[idx + len(sep):].strip()
            title = title[:idx].strip()
            break

    # Clean trailing recruitment noise from company name
    if company:
        for noise in (" tuyển dụng", " tuyển", " tuyển gấp", " - hạn nộp"):
            ci = company.lower().find(noise)
            if ci != -1:
                company = company[:ci].strip()

    return title.strip(), company.strip()


def _search_one_site(domain: str, label: str, q: str,
                     city: Optional[str], max_n: int) -> List[dict]:
    """Search a single site using DDGS, run in a thread to avoid blocking."""
    import time
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        city_term = city if city and city not in ("Tất cả", "") else ""
        # Simple, short query — works reliably across all DDGS backends
        query = f"{q} {city_term} site:{domain}".strip()
        print(f"  [{label}] '{query}'", flush=True)

        raw = []
        for attempt in range(2):
            try:
                with DDGS() as ddgs:
                    # No timelimit — avoids 0-result bug with Vietnamese text + Google backend
                    raw = list(ddgs.text(query, max_results=max_n))
                break
            except Exception as e:
                print(f"  [{label}] attempt {attempt + 1} failed: {e}", flush=True)
                if attempt == 0:
                    time.sleep(1.2)

        kept = []
        for r in raw:
            url = r.get("href", "")
            if not url or not _is_job_detail_url(url):
                continue
            raw_title = r.get("title", "")
            parsed_title, parsed_company = _parse_job_title_and_company(raw_title)
            kept.append(_make_job(
                id="",  # assigned later
                title=parsed_title or _clean_title(raw_title),
                company=parsed_company or "N/A",
                location=_extract_location(r.get("body", "")),
                location_type="domestic",
                work_model="on-site",
                url=url,
                source=label,
                description=r.get("body", ""),
                posted_at=None,
                salary="",
                tags=[],
            ))
        print(f"  [{label}] {len(raw)} raw → {len(kept)} job details", flush=True)
        return kept
    except Exception as e:
        import traceback
        print(f"  [{label}] ERR: {e}", flush=True)
        traceback.print_exc()
        return []


async def _fetch_domestic_ddgs(q: str, city: Optional[str]) -> List[dict]:
    import asyncio
    print(f"\n[DOMESTIC] q='{q}' city='{city}'", flush=True)
    logger.info(f"Domestic search: q={q!r} city={city!r}")

    all_results: List[dict] = []
    seen_urls: set = set()

    # Sequential per-site searches — avoids simultaneous DDGS rate-limits
    for domain, label, max_n in _SITE_CONFIGS:
        site_jobs = await asyncio.to_thread(
            _search_one_site, domain, label, q, city, max_n
        )
        for job in site_jobs:
            url = job.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(job)

    # HEAD-check: loại link chết/redirect homepage trước khi trả về
    # (Semaphore tránh burst request vào 1 site; soft-404 check ở tầng verify Jina)
    verified: List[dict] = []
    if all_results:
        sem = asyncio.Semaphore(6)
        from app.utils.link_check import is_article_accessible as _check

        async def _guarded(job, client):
            async with sem:
                return job, await _check(job.get("url", ""), client)

        async with httpx.AsyncClient() as client:
            checks = await asyncio.gather(*[
                _guarded(job, client) for job in all_results
            ])
        dead_by_site: dict = {}
        for job, (ok, reason) in checks:
            if ok:
                job["id"] = f"ddg-{len(verified)}"
                verified.append(job)
            else:
                site = job.get("source", "?")
                dead_by_site[site] = dead_by_site.get(site, 0) + 1
                logger.info(f"Domestic HEAD-check loại link chết [{site}]: {reason} — {job.get('url', '')}")
        if dead_by_site:
            print(f"[DOMESTIC] HEAD-check loại {len(all_results) - len(verified)} link chết: {dead_by_site}", flush=True)

    print(f"[DOMESTIC] Done: {len(verified)} unique jobs from {len(_SITE_CONFIGS)} sites.\n", flush=True)
    logger.info(f"Domestic search complete: {len(verified)} jobs.")
    return verified


# Verify tự động ngay lúc search (không cần nút bấm tay):
# chỉ verify N job đầu để tránh chậm (mỗi job 1 lần fetch Jina, chạy song song).
_TOP_VERIFY_COUNT = 10
_VERIFY_CONCURRENCY = 4

_VERIFY_DEFAULTS = {
    "deadline_status": "UNKNOWN",
    "deadline_date": None,
    "legit_flag": "UNKNOWN",
    "legit_reason": "",
    "verified": False,
}


async def _verify_top_jobs(jobs: List[dict], limit: int = _TOP_VERIFY_COUNT) -> None:
    """Gắn deadline/legit/posted_at vào N job đầu tiên (mutate tại chỗ)."""
    import asyncio
    from app.services.job_verifier import fetch_and_verify_job

    for job in jobs:
        job.update({k: v for k, v in _VERIFY_DEFAULTS.items() if k not in job})
        if job.get("posted_at"):
            job["posted_at_verified"] = False

    targets = jobs[:limit]
    if not targets:
        return
    sem = asyncio.Semaphore(_VERIFY_CONCURRENCY)

    async def _guarded(job: dict):
        async with sem:
            try:
                return job, await fetch_and_verify_job(job.get("url", ""))
            except Exception as e:
                logger.warning(f"Auto-verify lỗi [{job.get('url', '')}]: {e}")
                return job, {}

    print(f"[VERIFY] Auto-verify {len(targets)}/{len(jobs)} jobs đầu...", flush=True)
    for job, res in await asyncio.gather(*[_guarded(j) for j in targets]):
        if not res:
            continue
        job["deadline_status"] = res.get("deadline_status", "UNKNOWN")
        job["deadline_date"] = res.get("deadline_date")
        job["legit_flag"] = res.get("legit_flag", "UNKNOWN")
        job["legit_reason"] = res.get("legit_reason", "")
        if not job.get("posted_at") and res.get("posted_at"):
            job["posted_at"] = res["posted_at"]
            job["posted_at_verified"] = True
        job["verified"] = True
    n_ok = sum(1 for j in targets if j.get("verified"))
    print(f"[VERIFY] Xong: {n_ok}/{len(targets)} jobs có kết quả verify.", flush=True)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/jobs/search", summary="Tìm kiếm việc làm từ nhiều nguồn uy tín")
async def search_jobs(
    keyword: str = Query("", description="Vị trí tuyển dụng (VD: React, Python, Java)"),
    location_type: str = Query("domestic", description="'domestic' hoặc 'overseas'"),
    level: Optional[str] = Query(None, description="Trình độ (VD: Intern, Junior, Senior)"),
    city: Optional[str] = Query(None, description="Thành phố trong nước (VD: Hà Nội)"),
    sort: Optional[str] = Query(None, description="'newest' để sắp xếp tin mới nhất trước (4.4)"),
    db: AsyncSession = Depends(get_db),
):
    print(f"\n[SEARCH] keyword={keyword!r} type={location_type} level={level} city={city}", flush=True)
    logger.info(f"Job search: keyword={keyword!r} location_type={location_type} level={level} city={city}")

    variants = await _expand_queries(keyword, db)
    if len(variants) > 1:
        print(f"[SEARCH] Alias expansion: {variants}", flush=True)
    results: List[dict] = []
    seen_all: set = set()

    if location_type == "overseas":
        print("[SEARCH] Mode: overseas — calling all overseas APIs in parallel", flush=True)
        async with httpx.AsyncClient() as client:
            from asyncio import gather
            batches = await gather(*[
                fn(client, _build_search_terms(v, level))
                for v in variants
                for fn in (_fetch_remotive, _fetch_arbeitnow, _fetch_jobicy, _fetch_themuse)
            ])
            for batch in batches:
                for job in batch:
                    url = job.get("url", "")
                    if url and url not in seen_all:
                        seen_all.add(url)
                        results.append(job)
        print(f"[SEARCH] Overseas done: {len(results)} unique jobs", flush=True)

    elif location_type == "domestic":
        print("[SEARCH] Mode: domestic — per-site DDGS search", flush=True)
        for v in variants:
            q = _build_search_terms(v, level)
            print(f"[SEARCH] Effective query: {q!r}", flush=True)
            for job in await _fetch_domestic_ddgs(q, city):
                url = job.get("url", "")
                if url and url not in seen_all:
                    seen_all.add(url)
                    job["id"] = f"ddg-{len(results)}"
                    results.append(job)

    else:
        raise HTTPException(
            status_code=400,
            detail="location_type không hợp lệ. Dùng 'domestic' hoặc 'overseas'.",
        )

    before = len(results)
    results = _post_filter_level(results, level)
    if len(results) != before:
        print(f"[SEARCH] Level post-filter: {before} → {len(results)} (level={level!r})", flush=True)

    await _verify_top_jobs(results)

    print(f"[SEARCH] ✓ Returning {len(results)} jobs\n", flush=True)
    if sort == "newest":
        # posted_at ISO — job thiếu ngày đăng xếp cuối
        results.sort(key=lambda j: j.get("posted_at") or "", reverse=True)
    return {"message": f"Tìm thấy {len(results)} công việc.", "data": results}


# ── Job Verify (deadline + legit) ────────────────────────────────────────────

class VerifyRequest(BaseModel):
    url: str
    deep: bool = False  # True → bật thêm LLM fallback (Tầng C)


@router.post("/api/jobs/verify", summary="Kiểm tra hạn nộp + dấu hiệu lừa đảo của 1 job")
async def verify_job(payload: VerifyRequest):
    from app.services.job_verifier import fetch_and_verify_job
    if not payload.url or not payload.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL không hợp lệ.")
    result = await fetch_and_verify_job(payload.url, deep=payload.deep)
    return {"message": "Đã kiểm tra.", "data": {"url": payload.url, **result}}


@router.post("/api/jobs/{job_ref}/verify", summary="Verify job theo URL (percent-encoded) trong path")
async def verify_job_by_ref(job_ref: str, deep: bool = False):
    """job_ref = URL tin tuyển dụng đã percent-encode (vd dùng encodeURIComponent).
    Giữ endpoint body /api/jobs/verify làm alias gọn hơn."""
    import urllib.parse
    from app.services.job_verifier import fetch_and_verify_job
    url = urllib.parse.unquote(job_ref)
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL trong path không hợp lệ (cần percent-encode).")
    result = await fetch_and_verify_job(url, deep=deep)
    return {"message": "Đã kiểm tra.", "data": {"url": url, **result}}


# ── Job Watch ─────────────────────────────────────────────────────────────────

@router.get("/api/jobs/watch", summary="Danh sách vị trí việc làm đang quan tâm")
async def get_job_watches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobWatch).order_by(JobWatch.id.desc()))
    items = result.scalars().all()
    return {"message": f"{len(items)} vị trí đang theo dõi.", "data": [i.to_dict() for i in items]}


@router.post("/api/jobs/watch", summary="Thêm vị trí việc làm vào danh sách quan tâm", status_code=201)
async def add_job_watch(
    position: str = Query(..., description="Tên vị trí (VD: Frontend React)"),
    level: Optional[str] = Query(None, description="Trình độ (VD: Junior)"),
    location_type: str = Query("domestic"),
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    item = JobWatch(
        position=position,
        level=level or "Tất cả",
        location_type=location_type,
        city=city or "Tất cả",
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"message": f"Đã thêm '{position}' vào danh sách quan tâm.", "data": item.to_dict()}


@router.delete("/api/jobs/watch/{watch_id}", summary="Xóa vị trí khỏi danh sách quan tâm")
async def delete_job_watch(watch_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobWatch).where(JobWatch.id == watch_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vị trí.")
    await db.delete(item)
    await db.commit()
    return {"message": "Đã xóa.", "data": {"id": watch_id}}
