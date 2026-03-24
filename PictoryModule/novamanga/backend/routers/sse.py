from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.sse_manager import sse_manager

router = APIRouter()


@router.get("/sse/tasks")
async def sse_tasks(ref_ids: str):
    ids = [r.strip() for r in ref_ids.split(",") if r.strip()]

    async def generator():
        async for chunk in sse_manager.stream(ids):
            yield chunk

    return StreamingResponse(generator(), media_type="text/event-stream")
