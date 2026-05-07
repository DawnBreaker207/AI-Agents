import re
import json
import logging

logger = logging.getLogger(__name__)


def parse_json_column(data, default_value=None):
    if data is None:
        return default_value if default_value is not None else []
    if isinstance(data, (list, dict)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return default_value if default_value is not None else []
    return default_value


def parse_xml_tag(text: str, tag: str) -> dict:
    """
    Trích xuất nội dung giữa các thẻ (ví dụ: <analysis>...</analysis>)
    và chuyển đổi sang Dictionary.
    """
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            logger.error(f"Lỗi parse JSON từ tag <{tag}>")
    return {}


def parse_analysis_tag(text: str) -> dict:
    """Trích xuất và parse JSON từ thẻ <analysis>"""
    pattern = r"<analysis>(.*?)</analysis>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            logger.error("Không thể parse JSON từ Stage 3")
    return {}
