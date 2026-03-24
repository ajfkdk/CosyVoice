from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from db import project_db

router = APIRouter()


class UpdateZoneReq(BaseModel):
    order_index: int | None = None
    text_content: str | None = None
    emotion_primary: str | None = None
    emotion_intensity: float | None = None
    prompt_positive: str | None = None
    prompt_negative: str | None = None


@router.get("/chapters/{cid}/zones")
async def list_zones(cid: str, project_path: str):
    return project_db.list_zones(project_path, cid)


@router.get("/zones/{zid}")
async def get_zone(zid: str, project_path: str):
    z = project_db.get_zone(project_path, zid)
    if not z:
        raise HTTPException(404)
    return z


@router.put("/zones/{zid}")
async def update_zone(zid: str, req: UpdateZoneReq, project_path: str):
    kwargs = {k: v for k, v in req.model_dump().items() if v is not None}
    return project_db.update_zone(project_path, zid, **kwargs)


@router.post("/zones/{zid}/prompt/generate")
async def generate_prompt(zid: str, project_path: str):
    import json as _json
    zone = project_db.get_zone(project_path, zid)
    if not zone:
        raise HTTPException(404)

    chapter = project_db.get_chapter(project_path, zone["chapter_id"])
    story_context = chapter.get("raw_text", "") if chapter else ""

    chars = _json.loads(zone.get("characters_present", "[]"))
    char_variants = []
    all_chars = project_db.list_all_characters(project_path)
    for name in chars:
        for ch in all_chars:
            if ch["name"] == name:
                variants = project_db.list_character_variants(project_path, ch["id"])
                if variants:
                    v = variants[0]
                    char_variants.append({
                        "name": name,
                        "trigger_words": _json.loads(v.get("trigger_words", "[]")),
                        "appearance_summary": v.get("appearance_summary", ""),
                    })

    task = project_db.enqueue_task(
        project_path, "xiao_qiao_prompt",
        {
            "zone_id": zid,
            "zone_text": zone["text_content"],
            "emotion_primary": zone["emotion_primary"],
            "emotion_intensity": zone["emotion_intensity"],
            "story_context": story_context,
            "character_variants": char_variants,
        },
        reference_id=zid,
        reference_type="zone"
    )
    return {"task_id": task["id"]}


@router.post("/zones/{zid}/image/generate")
async def generate_image(zid: str, project_path: str, body: dict = None):
    zone = project_db.get_zone(project_path, zid)
    if not zone:
        raise HTTPException(404)
    body = body or {}
    prompt_pos = body.get("prompt_positive") or zone.get("prompt_positive", "")
    if not prompt_pos:
        raise HTTPException(400, "请先生成 prompt 或提供 prompt_positive")
    task = project_db.enqueue_task(
        project_path, "nanobanana_generate",
        {
            "zone_id": zid,
            "prompt_positive": prompt_pos,
            "prompt_negative": body.get("prompt_negative") or zone.get("prompt_negative", ""),
            "reference_images": body.get("reference_images", []),
        },
        reference_id=zid,
        reference_type="zone"
    )
    return {"task_id": task["id"]}


@router.get("/tasks/{task_id}")
async def get_task(task_id: str, project_path: str):
    t = project_db.get_task(project_path, task_id)
    if not t:
        raise HTTPException(404)
    return t


@router.get("/zones/{zid}/image")
async def get_zone_image(zid: str, project_path: str):
    with project_db.get_conn(project_path) as conn:
        row = conn.execute(
            "SELECT file_path FROM image_assets WHERE zone_id=? ORDER BY created_at DESC LIMIT 1",
            [zid]
        ).fetchone()
    if not row:
        raise HTTPException(404, "暂无图片")
    file_path = Path(row[0])
    if not file_path.exists():
        raise HTTPException(404, "图片文件不存在")
    return FileResponse(str(file_path), media_type="image/png")
