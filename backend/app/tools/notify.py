import httpx
import logging
from app.core.config import settings


logger = logging.getLogger(__name__)

async def notify_urgent(message: str):
    """Gửi thông báo khẩn cấp tới Telegram"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram chưa được cấu hình, bỏ qua thông báo.")
        return "Cảnh báo: Chưa cấu hình Telegram."

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": f"🚨 [TSI ALERT]\n\n{message}",
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            return "Đã gửi thông báo thành công."
        except Exception as e:
            logger.error(f"Lỗi gửi Telegram: {e}")
            return f"Lỗi gửi Telegram: {str(e)}"
