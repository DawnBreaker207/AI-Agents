import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.worker.scheduler import run_pipeline

logger = logging.getLogger(__name__)

class MaestroOrchestrator:
    def __init__(self):
        pass

    async def execute_workflow(self, topic: str, db: AsyncSession):
        logger.info(f"🚀 Bắt đầu gọi Pipeline mới (TSI Pipeline) bỏ qua topic: {topic}")
        
        # Gọi thẳng pipeline mới
        await run_pipeline()
        
        logger.info(f"✅ Hoàn thành gọi TSI Pipeline mới!")
        return {"status": "success", "msg": "Đã chạy pipeline mới thành công."}
