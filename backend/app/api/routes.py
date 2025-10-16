from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.schemas import Satellite

router = APIRouter()


@router.get("/")
async def root():
    return {
        "title": "AstroBridge",
        "version": "0.0.1",
        "description": "",
        "endpoints": {
            "": "",
        },
    }


@router.get("/satellites")
async def get_satellites(db: Session = Depends(get_db)):
    satellites = db.query(Satellite).all()
    return satellites


@router.post("/satellites")
async def create_satellite(db: Session = Depends(get_db)):
    mock_satellite = Satellite(
        intldes="2025-001A",
        satname="MockSat-1",
        country="USA",
        launch_piece="A",
        current="Y",
        object_name="MockSat-1",
        object_id="2025-001A",
    )
    db.add(mock_satellite)
    db.commit()
    db.refresh(mock_satellite)
    return mock_satellite
