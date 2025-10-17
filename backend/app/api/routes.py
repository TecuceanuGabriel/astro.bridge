from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.schemas import Satellite, TLE, RF

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


@router.get("/tles")
async def get_tles(db: Session = Depends(get_db)):
    tles = db.query(TLE).all()
    return tles


@router.get("/rfs")
async def get_rf(db: Session = Depends(get_db)):
    rf = db.query(RF).all()
    return rf
