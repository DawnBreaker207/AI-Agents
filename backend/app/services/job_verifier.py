"""Verify job: deadline scan (Tầng A) + scam red-flag scan (Tầng B) dùng chung
1 lần fetch content qua Jina. Tầng C (LLM) chỉ chạy khi deep=True."""
import logging
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

_VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# Tầng A — cụm khẳng định trực tiếp job đã đóng (kèm biến thể không dấu)
EXPIRED_PHRASES = [
    "đã hết hạn", "da het han", "hết hạn nộp hồ sơ", "het han nop ho so",
    "tin đã đóng", "tin da dong",
    "expired", "position filled", "no longer accepting",
]

# Tầng A — nhãn đi kèm ngày hết hạn
DEADLINE_LABELS = [
    "hạn nộp", "han nop", "hạn ứng tuyển", "han ung tuyen",
    "deadline", "apply by", "closing date",
]

# 4.4 — nhãn ngày đăng tin (lấy cùng 1 lần fetch với verify)
POSTED_LABELS = [
    "ngày đăng", "ngay dang", "đăng ngày", "dang ngay", "đăng lúc",
    "posted", "published",
]

# Tầng B — cụm nghi vấn lừa đảo (kèm biến thể không dấu)
SCAM_PHRASES = [
    "đóng phí", "dong phi", "nộp phí hồ sơ", "nop phi ho so",
    "phí đào tạo", "phi dao tao", "cọc đồng phục", "coc dong phuc",
    "phí giữ chỗ", "phi giu cho", "chuyển khoản trước", "chuyen khoan truoc",
    "nộp qua stk", "nop qua stk",
]

_DATE_PATTERN = re.compile(
    r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}"
)


def _parse_deadline_date(raw: str) -> datetime | None:
    try:
        import dateparser
    except ImportError:
        logger.warning("dateparser chưa cài — bỏ qua parse ngày deadline")
        return None
    dt = dateparser.parse(
        raw,
        settings={"TIMEZONE": "Asia/Ho_Chi_Minh", "TO_TIMEZONE": "UTC",
                  "RETURN_AS_TIMEZONE_AWARE": True, "DATE_ORDER": "DMY"},
    )
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_VN_TZ).astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)


def _vn_date_iso(dt: datetime) -> str:
    """Ngày theo giờ VN (tránh lệch ngày khi đổi sang UTC)."""
    return dt.astimezone(_VN_TZ).date().isoformat()


def _scan_deadline(content: str) -> tuple[str, str | None]:
    lowered = content.lower()
    for phrase in EXPIRED_PHRASES:
        if phrase in lowered:
            return "EXPIRED", None

    lowered_labels = [label.lower() for label in DEADLINE_LABELS]
    for label in lowered_labels:
        idx = lowered.find(label)
        if idx == -1:
            continue
        window = content[max(0, idx - 20):idx + 120]
        match = _DATE_PATTERN.search(window)
        if match:
            parsed = _parse_deadline_date(match.group(0))
            if parsed is None:
                continue
            if parsed < datetime.now(timezone.utc):
                return "EXPIRED", _vn_date_iso(parsed)
            return "OPEN", _vn_date_iso(parsed)

    # Fallback: ngày lẻ không kèm nhãn — chỉ nhận nếu duy nhất 1 ngày trong content
    lone_dates = _DATE_PATTERN.findall(content)
    if len(lone_dates) == 1:
        parsed = _parse_deadline_date(lone_dates[0])
        if parsed is not None:
            status = "EXPIRED" if parsed < datetime.now(timezone.utc) else "OPEN"
            return status, _vn_date_iso(parsed)

    return "UNKNOWN", None


def _scan_posted_date(content: str) -> str | None:
    """4.4 — ngày đăng thật từ trang chi tiết (cùng 1 lần fetch với verify)."""
    lowered = content.lower()
    for label in POSTED_LABELS:
        idx = lowered.find(label)
        if idx == -1:
            continue
        window = content[max(0, idx - 10):idx + 80]
        match = _DATE_PATTERN.search(window)
        if match:
            parsed = _parse_deadline_date(match.group(0))
            if parsed is not None:
                return _vn_date_iso(parsed)
    return None


def _scan_scam(content: str) -> tuple[str, str]:
    lowered = content.lower()
    for phrase in SCAM_PHRASES:
        if phrase in lowered:
            return "SUSPICIOUS", f"Khớp cụm: '{phrase}'"
    return "OK", ""


async def fetch_and_verify_job(url: str, deep: bool = False) -> dict:
    """Fetch content 1 lần, chạy Tầng A + B. Tầng C (LLM) chỉ khi deep=True."""
    from app.services.pipeline.stage3_deep import _fetch_full_content

    content, is_valid, fetch_reason = await _fetch_full_content(url)
    if not is_valid:
        return {
            "deadline_status": "UNKNOWN",
            "deadline_date": None,
            "posted_at": None,
            "legit_flag": "UNKNOWN",
            "legit_reason": f"Không đọc được nội dung trang: {fetch_reason}",
        }

    deadline_status, deadline_date = _scan_deadline(content)
    legit_flag, legit_reason = _scan_scam(content)
    posted_at = _scan_posted_date(content)

    # Tầng C — LLM fallback: chỉ khi A/B đều mơ hồ và client yêu cầu deep
    if deep and deadline_status == "UNKNOWN" and legit_flag == "OK":
        try:
            from app.core.brain import BrainService
            brain = BrainService()
            messages = [
                {"role": "system", "content":
                 "Bạn đánh giá tin tuyển dụng. Trả về JSON: "
                 '{"legit_score": 1-10, "reason": "..."}. '
                 "Điểm thấp = dấu hiệu lừa đảo (thu phí, stk cá nhân, lương bất thường)."},
                {"role": "user", "content": content[:3000]},
            ]
            import json
            raw = await brain.call_ai_async(messages, model_tier="low", force_json=True)
            parsed = json.loads(raw or "{}")
            score = float(parsed.get("legit_score", 10))
            reason = str(parsed.get("reason", ""))
            if score < 5:
                legit_flag, legit_reason = "SUSPICIOUS", f"LLM legit_score={score}: {reason}"[:300]
        except Exception as e:
            logger.error(f"Job verify LLM fallback lỗi: {e}")

    return {
        "deadline_status": deadline_status,
        "deadline_date": deadline_date,
        "posted_at": posted_at,
        "legit_flag": legit_flag,
        "legit_reason": legit_reason,
    }
