import json
import re
import logging
from app.core.brain import BrainService
from app.core.prompt import STAGE3_REACT_PROMPT
from app.tools.web_search import search_the_web
from app.tools.notify import notify_urgent
from core.utils import parse_xml_tag

logger = logging.getLogger(__name__)


class DeepAnalysisStage:
    def __init__(self):
        self.brain = BrainService()

    def _extract_impact_score(self, text: str) -> int:
        """Trích xuất điểm ảnh hưởng bằng Regex từ nội dung Finalize"""
        match = re.search(r"Impact Score:\s*(\d+)", text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 1), 10)  # Đảm bảo score nằm trong [1, 10]
        return 5

    async def run(self, filtered_signals: list) -> dict:
        messages = [
            {"role": "system", "content": STAGE3_REACT_PROMPT},
            {"role": "user", "content": json.dumps(filtered_signals, ensure_ascii=False)}
        ]

        logger.info("🧠 Stage 3: Bắt đầu vòng lặp ReAct phân tích chuyên sâu...")

        for i in range(5):
            # Dùng High-reasoning Model để suy luận
            response = self.brain.call_ai(messages, model_tier="high")

            # KIỂM TRA TRẠNG THÁI KẾT THÚC (Finalize)
            if "<analysis>" in response:
                extracted_data = parse_xml_tag(response, "analysis")

                # Ưu tiên lấy text từ JSON, nếu không có mới dùng split
                final_content = extracted_data.get("deep_analysis_text")
                if not final_content:
                    if "Finalize:" in response:
                        final_content = response.split("Finalize:")[-1].strip()
                    else:
                        # Nếu không có cả key lẫn keyword, lấy đại nội dung trong thẻ hoặc response thô
                        final_content = str(extracted_data)

                final_content = re.sub(r"<analysis>.*?</analysis>", "", final_content, flags=re.DOTALL).strip()

                logger.info(f"✅ Stage 3 hoàn tất. Score: {extracted_data.get('impact_score')}")
                return {
                    "status": "success",
                    "analysis": final_content,
                    "impact_score": extracted_data.get("impact_score", 5),
                    "raw_json": extracted_data
                }

            # XỬ LÝ HÀNH ĐỘNG (Action)
            action_match = re.search(r"Action:\s*([A-Z_]+)\((.*?)\)", response)
            if action_match:
                tool_name = action_match.group(1)
                args = action_match.group(2).strip("\"'")

                logger.info(f"🛠 Agent gọi Tool: {tool_name} với args: {args}")

                observation = ""
                if tool_name == "SEARCH_MORE":
                    search_results = search_the_web(args)
                    observation = json.dumps(search_results, ensure_ascii=False)
                elif tool_name == "NOTIFY_URGENT":
                    await notify_urgent(args)
                    observation = "Đã gửi thông báo khẩn cấp tới Telegram."
                else:
                    observation = f"Lỗi: Tool {tool_name} không tồn tại."

                # Lưu vết suy luận vào context
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
            else:
                # Nếu AI không gọi tool và cũng không Finalize, ép nó phải kết thúc hoặc nhắc nhở
                messages.append(
                    {"role": "user", "content": "Hãy đưa ra kết luận cuối cùng bằng định dạng Finalize: ..."})

        # Trường hợp xấu nhất: Bị lặp quá 5 lần
        logger.warning("⚠️ Stage 3: Vòng lặp đạt giới hạn nhưng không thể Finalize.")
        return {
            "status": "error",
            "analysis": "Không thể tổng hợp báo cáo do thiếu dữ liệu hoặc lỗi suy luận vòng lặp.",
            "impact_score": 1
        }
