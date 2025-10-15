from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    """GeoJSON-style bounding box"""
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)

class DateRange(BaseModel):
    start: datetime
    end: datetime

class SatelliteInfo(BaseModel):
    name: str
    provider: str
    sensor_type: str
    orbit_type: Optional[str] = None

class UnifiedSatelliteImage(BaseModel):
    """Unified data model for satellite imagery"""
    id: str 
    timestamp: datetime
    bbox: BoundingBox
    satellite: SatelliteInfo
    bands: List[str]
    resolution_meters: float
    cloud_coverage: Optional[float] = None
    source_provider: str
    source_id: str
    source_url: str
    preview_url: Optional[str] = None
    quality_score: float = Field(default=0.0, ge=0.0, le=100.0)

class SearchQuery(BaseModel):
    bbox: BoundingBox
    date_range: DateRange
    max_cloud_coverage: Optional[float] = 30.0
    min_resolution: Optional[float] = None  # meters
