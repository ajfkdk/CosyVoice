from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import projects
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pictory API")
app.include_router(projects.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/assets/characters", exist_ok=True)
os.makedirs("data/assets/audio", exist_ok=True)
os.makedirs("data/assets/images", exist_ok=True)

app.mount("/assets", StaticFiles(directory="data/assets"), name="assets")

@app.get("/")
def root():
    return {"message": "Pictory API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
