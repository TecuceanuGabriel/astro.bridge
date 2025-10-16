from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.db import Base, engine, get_db
from .worker import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AstroBridge", version="0.0.1", description="")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    start_scheduler()


app.include_router(router)
