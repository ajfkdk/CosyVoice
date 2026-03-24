import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import projects, chapters, zones, characters, sse
from db import global_db
from services.task_runner import get_runner

app = FastAPI(title="NovaManga API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(sse.router, prefix="/api")

STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.on_event("startup")
async def startup():
    for p in global_db.list_projects():
        runner = get_runner(p["path"])
        asyncio.create_task(runner.start())


@app.get("/api/assets")
async def serve_asset(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(404)
    return FileResponse(str(p))


@app.get("/health")
async def health():
    return {"status": "ok"}
