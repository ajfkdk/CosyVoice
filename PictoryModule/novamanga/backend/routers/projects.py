from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import global_db, project_db
from services.task_runner import get_runner
import asyncio

router = APIRouter()


class CreateProjectReq(BaseModel):
    name: str
    path: str


@router.post("/projects")
async def create_project(req: CreateProjectReq):
    p = global_db.create_project(req.name, req.path)
    runner = get_runner(p["path"])
    asyncio.create_task(runner.start())
    return p


@router.get("/projects")
async def list_projects():
    return global_db.list_projects()


@router.get("/projects/{pid}")
async def get_project(pid: str):
    p = global_db.get_project(pid)
    if not p:
        raise HTTPException(404)
    return p
