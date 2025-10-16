from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.db.models_db import Satellite

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
    mock_satellite = Satellite(norad_id=1, name="Mock Satellite")
    db.add(mock_satellite)
    db.commit()
    db.refresh(mock_satellite)
    return mock_satellite
