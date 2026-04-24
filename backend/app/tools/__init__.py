from app.tools.web_scraper import get_web_content
from app.tools.web_search import search_the_web

TOOL_REGISTRY = {
    "read_web_content": {
        "func": get_web_content,
        "description": "Đọc nội dung chi tiết từ một URL của trang web. Chỉ sử dụng khi bạn đã có một URL cụ thể."
    },
    "search_the_web": {
        "func": search_the_web,
        "description": "Tìm kiếm trên Internet với một câu truy vấn để lấy danh sách các trang web liên quan. Hữu ích khi bạn cần tìm thông tin nhưng chưa biết bắt đầu từ đâu."
    }
}
