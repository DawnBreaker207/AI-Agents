from fastapi import APIRouter
from app.api.agent import agent_router

api_router = APIRouter()

@api_router.get("/")
async def root():
    return {"message": "AI Agent Backend is running!"}


api_router.include_router(
    agent_router,
    prefix="/api/v1",
    tags=["Agent Operations"]
)
