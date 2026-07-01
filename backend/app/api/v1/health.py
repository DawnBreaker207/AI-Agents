import logging

from fastapi import APIRouter

from app.schemas.common import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", summary="Check agent status")
async def health_check():
    return APIResponse(
        message="Hệ thống đang hoạt động ổn định.",
        data={"status": "running", "agent": "GlobalTechTalentAgent-01"}
    )
