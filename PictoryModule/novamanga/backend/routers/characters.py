from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import global_db, project_db

router = APIRouter()


class CreateCharacterReq(BaseModel):
    name: str
    raw_description: str = ""


@router.post("/projects/{pid}/characters")
async def create_character(pid: str, req: CreateCharacterReq, project_path: str):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    char = project_db.create_character(project_path, pid, req.name, req.raw_description)
    if req.raw_description.strip():
        project_db.enqueue_task(
            project_path, "xiao_ming_extract",
            {"character_id": char["id"], "character_name": req.name, "raw_description": req.raw_description},
            reference_id=char["id"],
            reference_type="character"
        )
    return char


@router.get("/projects/{pid}/characters")
async def list_characters(pid: str, project_path: str):
    return project_db.list_characters(project_path, pid)


@router.get("/characters/{char_id}/variants")
async def list_variants(char_id: str, project_path: str):
    return project_db.list_character_variants(project_path, char_id)
