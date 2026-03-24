from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import global_db, project_db

router = APIRouter()


class CreateChapterReq(BaseModel):
    title: str
    order_index: int = 0


class UpdateChapterReq(BaseModel):
    title: str | None = None
    raw_text: str | None = None
    order_index: int | None = None


@router.post("/projects/{pid}/chapters")
async def create_chapter(pid: str, req: CreateChapterReq):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return project_db.create_chapter(p["path"], pid, req.title, req.order_index)


@router.get("/projects/{pid}/chapters")
async def list_chapters(pid: str):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return project_db.list_chapters(p["path"])


@router.put("/chapters/{cid}")
async def update_chapter(cid: str, req: UpdateChapterReq, project_path: str):
    kwargs = {k: v for k, v in req.model_dump().items() if v is not None}
    return project_db.update_chapter(project_path, cid, **kwargs)


@router.post("/chapters/{cid}/parse")
async def parse_chapter(cid: str, project_path: str):
    chapter = project_db.get_chapter(project_path, cid)
    if not chapter:
        raise HTTPException(404)

    raw_text = chapter["raw_text"]
    if not raw_text.strip():
        raise HTTPException(400, "章节内容为空")

    blocks = _split_blocks(raw_text, max_chars=1000)
    task_ids = []
    base_order = 0

    for i, (block_text, base_offset) in enumerate(blocks):
        prev_text = blocks[i - 1][0][-100:] if i > 0 else ""
        next_text = blocks[i + 1][0][:100] if i < len(blocks) - 1 else ""

        task = project_db.enqueue_task(
            project_path, "liu_bei_parse",
            {
                "chapter_id": cid,
                "block_text": block_text,
                "overlap_prev": prev_text,
                "overlap_next": next_text,
                "base_offset": base_offset,
                "base_order": base_order,
            },
            reference_id=cid,
            reference_type="chapter"
        )
        task_ids.append(task["id"])
        base_order += 50

    project_db.update_chapter(project_path, cid, parse_status="processing")
    return {"task_ids": task_ids}


def _split_blocks(text: str, max_chars: int) -> list[tuple[str, int]]:
    paragraphs = text.split("\n")
    blocks, current, offset, current_offset = [], [], 0, 0

    for para in paragraphs:
        if sum(len(p) for p in current) + len(para) > max_chars and current:
            block_text = "\n".join(current)
            blocks.append((block_text, current_offset))
            current_offset = offset
            current = []
        current.append(para)
        offset += len(para) + 1

    if current:
        blocks.append(("\n".join(current), current_offset))
    return blocks
