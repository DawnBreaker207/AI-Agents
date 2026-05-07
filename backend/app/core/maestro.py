import logging
from sqlalchemy.orm import Session
from app.stages.stage1_scout import ScoutStage
from app.stages.stage2_filter import FilterStage
from app.stages.stage3_deep import DeepAnalysisStage
from app.stages.stage4_writer import WriterStage
from app.tools.database_ops import save_to_dashboard
from core.utils import parse_xml_tag

logger = logging.getLogger(__name__)


class MaestroOrchestrator:
    def __init__(self):
        self.scout = ScoutStage()
        self.filter = FilterStage()
        self.deep = DeepAnalysisStage()
        self.writer = WriterStage()

    async def execute_workflow(self, topic: str, db: Session):
        logger.info(f"🚀 Bắt đầu TSI Pipeline cho: {topic}")

        # STAGE 1: Thu thập dữ liệu thô
        raw_data = await self.scout.run(topic)
        if not raw_data:
            return {"status": "skipped", "msg": "Không có tin tức kích hoạt bẫy."}

        # STAGE 2: Lọc tin chất lượng cao
        signals = self.filter.run(raw_data)
        high_priority = [s for s in signals if s.get("priority_score", 0) >= 7]
        if not high_priority:
            return {"status": "skipped", "msg": "Điểm ưu tiên thấp, hủy phân tích."}

        # STAGE 3: Phân tích sâu (Trả về chuỗi có thẻ <analysis>)
        deep_result = await self.deep.run(high_priority)
        if deep_result.get("status") == "error":
            return {"status": "error", "msg": deep_result.get("analysis")}
        # Trích xuất dữ liệu JSON từ Stage 3
        extracted_data = deep_result.get("raw_json", {})

        # STAGE 4: Biên tập báo cáo
        # Lấy phần text phân tích sạch từ JSON để Writer biên tập,
        # tránh đưa nguyên đống JSON cho Writer.
        analysis_text = deep_result.get("analysis", "")
        final_report = self.writer.run({"analysis": analysis_text})

        # Xử lý tags duy nhất (Unique)
        unique_tags = list(set([tag for s in high_priority for tag in s.get("keywords", [])]))

        # CHUẨN BỊ DỮ LIỆU LƯU TRỮ
        db_data = {
            "title": f"Báo cáo chiến lược: {topic}",
            "summary": final_report,  # Nội dung Markdown bài viết
            "impact_score": extracted_data.get("impact_score", 5),
            "tags": unique_tags,
            "raw_analysis": extracted_data,  # Lưu toàn bộ JSON gốc để API dùng
            "url": high_priority[0].get("url", "") if high_priority else ""
        }

        report_record = save_to_dashboard(db, db_data)

        logger.info(f"✅ Hoàn thành TSI Pipeline! ID: {report_record.id}")
        return {"status": "success", "report_id": report_record.id}
