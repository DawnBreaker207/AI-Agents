import logging
import os
import re as _re
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends
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
        r = await client.get(
            "https://www.themuse.com/api/public/jobs",
            params={"category": "Engineering", "level": "Entry Level", "page": 0},
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
                location=city_term or "Việt Nam",
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
                job["id"] = f"ddg-{len(all_results)}"
                all_results.append(job)

    print(f"[DOMESTIC] Done: {len(all_results)} unique jobs from {len(_SITE_CONFIGS)} sites.\n", flush=True)
    logger.info(f"Domestic search complete: {len(all_results)} jobs.")
    return all_results


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/jobs/search", summary="Tìm kiếm việc làm từ nhiều nguồn uy tín")
async def search_jobs(
    keyword: str = Query("", description="Vị trí tuyển dụng (VD: React, Python, Java)"),
    location_type: str = Query("domestic", description="'domestic' hoặc 'overseas'"),
    level: Optional[str] = Query(None, description="Trình độ (VD: Intern, Junior, Senior)"),
    city: Optional[str] = Query(None, description="Thành phố trong nước (VD: Hà Nội)"),
):
    print(f"\n[SEARCH] keyword={keyword!r} type={location_type} level={level} city={city}", flush=True)
    logger.info(f"Job search: keyword={keyword!r} location_type={location_type} level={level} city={city}")

    q = _build_search_terms(keyword, level)
    print(f"[SEARCH] Effective query: {q!r}", flush=True)
    results: List[dict] = []

    if location_type == "overseas":
        print("[SEARCH] Mode: overseas — calling all overseas APIs in parallel", flush=True)
        async with httpx.AsyncClient() as client:
            from asyncio import gather
            batches = await gather(
                _fetch_remotive(client, q),
                _fetch_arbeitnow(client, q),
                _fetch_jobicy(client, q),
                _fetch_themuse(client, q),
            )
            seen: set = set()
            for batch in batches:
                for job in batch:
                    url = job.get("url", "")
                    if url and url not in seen:
                        seen.add(url)
                        results.append(job)
        print(f"[SEARCH] Overseas done: {len(results)} unique jobs", flush=True)

    elif location_type == "domestic":
        print("[SEARCH] Mode: domestic — per-site DDGS search", flush=True)
        results = await _fetch_domestic_ddgs(q, city)

    else:
        raise HTTPException(
            status_code=400,
            detail="location_type không hợp lệ. Dùng 'domestic' hoặc 'overseas'.",
        )

    print(f"[SEARCH] ✓ Returning {len(results)} jobs\n", flush=True)
    return {"message": f"Tìm thấy {len(results)} công việc.", "data": results}


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
