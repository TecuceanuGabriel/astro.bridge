from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.core.db import get_db

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}
