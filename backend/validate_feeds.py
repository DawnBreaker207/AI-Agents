"""
Kiểm tra TẤT CẢ RSS feed URLs trong RSS_SOURCES trước khi seed vào DB.
Chạy: python validate_feeds.py

Không ghi gì vào DB, chỉ in kết quả kiểm tra.
Không import từ seed_sources để tránh lỗi thiếu dependency.
"""
import ast
import asyncio
import sys
from typing import Optional

# Fix encoding cho console Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import feedparser
import httpx

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_HEADERS = {"User-Agent": _USER_AGENT}
_TIMEOUT = 10.0
_MAX_CONCURRENT = 10


def _extract_rss_sources(filepath: str = "seed_sources.py") -> list[dict]:
    """Đọc RSS_SOURCES từ file seed_sources.py bằng AST (không import module)."""
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RSS_SOURCES":
                    return ast.literal_eval(node.value)

    raise ValueError("Không tìm thấy RSS_SOURCES trong seed_sources.py")


async def check_single_feed(
    sem: asyncio.Semaphore,
    client: httpx.AsyncClient,
    source: dict,
) -> dict:
    """Kiểm tra một RSS feed URL, trả về dict kết quả."""
    name = source["name"]
    url = source["url"]
    priority = source.get("priority_weight", 1.0)

    async with sem:
        result = {
            "name": name,
            "url": url,
            "priority": priority,
            "status": "ERROR",
            "entries": 0,
            "reason": "",
        }

        # Lần 1
        ok, resp_text, status_code, error_msg = await _fetch_feed(client, url)
        if not ok and "timeout" in error_msg.lower():
            # Retry 1 lần nếu timeout
            await asyncio.sleep(1)
            ok, resp_text, status_code, error_msg = await _fetch_feed(client, url)

        if not ok:
            result["status"] = "DEAD" if status_code and status_code >= 400 else "ERROR"
            result["reason"] = error_msg
            return result

        # Parse bằng feedparser
        feed = feedparser.parse(resp_text)
        bozo = feed.bozo
        bozo_exception = feed.get("bozo_exception")
        entries_count = len(feed.entries)

        # bozo == True => lỗi parse XML
        if bozo:
            exc_name = type(bozo_exception).__name__ if bozo_exception else "Unknown"
            # CharacterEncodingOverride là warning nhẹ, vẫn OK
            if "CharacterEncoding" in exc_name:
                pass
            else:
                result["status"] = "ERROR"
                result["reason"] = f"Bozo parse error: {exc_name}"
                result["entries"] = entries_count
                return result

        if entries_count == 0:
            result["status"] = "EMPTY"
            result["reason"] = "Feed co 0 entry"
            result["entries"] = 0
            return result

        result["status"] = "OK"
        result["entries"] = entries_count
        result["reason"] = ""
        return result


async def _fetch_feed(
    client: httpx.AsyncClient, url: str
) -> tuple[bool, str, Optional[int], str]:
    """GET feed URL, tra ve (ok, response_text, status_code, error_msg)."""
    try:
        resp = await client.get(url, headers=_HEADERS, follow_redirects=True, timeout=_TIMEOUT)
        if resp.status_code != 200:
            return False, "", resp.status_code, f"HTTP {resp.status_code}"
        return True, resp.text, resp.status_code, ""
    except httpx.TimeoutException:
        return False, "", None, "Timeout"
    except httpx.ConnectError:
        return False, "", None, "ConnectError: Khong the ket noi"
    except httpx.RequestError as e:
        return False, "", None, f"RequestError: {type(e).__name__}"
    except Exception as e:
        return False, "", None, f"Exception: {type(e).__name__}: {e}"


async def main():
    print("=" * 100)
    print("  RSS FEED VALIDATOR  Kiem tra tat ca nguon RSS truoc khi seed")
    print("=" * 100)

    RSS_SOURCES = _extract_rss_sources()
    print(f"  Tong so nguon: {len(RSS_SOURCES)}")
    print()

    sem = asyncio.Semaphore(_MAX_CONCURRENT)
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        tasks = [check_single_feed(sem, client, src) for src in RSS_SOURCES]
        results = await asyncio.gather(*tasks)

    # In bang ket qua
    header = f"{'STT':<4} {'Ten nguon':<28} {'Status':<8} {'Entries':<8} {'Priority':<9} URL"
    print(header)
    print("-" * len(header))

    ok_sources = []
    failed_sources = []

    for i, r in enumerate(results, 1):
        name_display = r["name"][:26] + ".." if len(r["name"]) > 26 else r["name"]
        status_display = r["status"]
        entries_display = str(r["entries"]) if r["entries"] else "-"
        priority_display = f"{r['priority']:.1f}"
        print(f"{i:<4} {name_display:<28} {status_display:<8} {entries_display:<8} {priority_display:<9} {r['url']}")

        if r["reason"]:
            print(f"     => Loi: {r['reason']}")

        if r["status"] == "OK":
            ok_sources.append(r)
        else:
            failed_sources.append(r)

    # Tong ket
    print()
    print("=" * 100)
    print(f"  OK: {len(ok_sources)} / {len(RSS_SOURCES)}")
    print(f"  Loi: {len(failed_sources)} / {len(RSS_SOURCES)}")
    print()

    # Danh sach nguon OK
    print("-" * 100)
    print("  Danh sach nguon OK (copy vao RSS_SOURCES):")
    print("-" * 100)
    print("RSS_SOURCES = [")
    for r in ok_sources:
        print(f'    {{"name": "{r["name"]}", "url": "{r["url"]}", "priority_weight": {r["priority"]}}},')
    print("]")
    print()

    # Danh sach nguon loi
    if failed_sources:
        print("-" * 100)
        print("  Danh sach nguon loi can loai bo hoac kiem tra lai:")
        print("-" * 100)
        for r in failed_sources:
            print(f'  - {r["name"]}: {r["url"]}  ({r["status"]} -- {r["reason"]})')

    return 0 if not failed_sources else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
