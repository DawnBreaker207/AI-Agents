from app.tools.web_tool import get_web_content

TOOL_REGISTRY = {
    "search_web": {
        "func": get_web_content,
        "description": "Lấy nội dung chi tiết từ một URL website"
    }
}
