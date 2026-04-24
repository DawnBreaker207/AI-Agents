from ddgs import DDGS
import json
import logging


def search_the_web(query: str):
    if not query:
        return "Lỗi: Cần có câu truy vấn để tìm kiếm."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "Không tìm thấy kết quả nào."

        simplified_results = []
        for r in results:
            simplified_results.append({
                "title": r.get('title'),
                "href": r.get('href'),
                "body": r.get('body')
            })

        return json.dumps(simplified_results, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error during web search for query '{query}': {e}")
        return f"Lỗi trong quá trình tìm kiếm: {str(e)}"
