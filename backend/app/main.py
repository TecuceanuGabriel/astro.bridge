from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
from enum import Enum
import asyncio

from app.adapters.adapter import SatelliteAPIAdapter
from app.adapters.NASAAdapter import NASAAdapter
from app.adapters.SentinelAdapter import SentinelAdapter
from app.adapters.APIRegistry import SatelliteAPIRegistry, MergeStrategy
from app.db.models import UnifiedSatelliteImage, SearchQuery

app = FastAPI(title="Unified Satellite API", version="0.0.1")

# Initialize registry
registry = SatelliteAPIRegistry()

@app.on_event("startup")
async def startup_event():
    """Initialize API adapters on startup"""
    # Register adapters
    registry.register_adapter("nasa", NASAAdapter(api_key="DEMO_KEY"))
    registry.register_adapter("sentinel", SentinelAdapter())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await registry.close_all()

@app.get("/")
async def root():
    return {
        "service": "Unified Satellite API",
        "version": "1.0.0",
        "providers": list(registry.adapters.keys())
    }

@app.post("/search", response_model=List[UnifiedSatelliteImage])
async def search_satellite_imagery(
    query: SearchQuery,
    strategy: MergeStrategy = MergeStrategy.BEST_QUALITY,
    limit: int = Query(default=20, le=100)
):
    """
    Search for satellite imagery across all providers
    
    - **bbox**: Bounding box for area of interest
    - **date_range**: Start and end dates
    - **max_cloud_coverage**: Maximum acceptable cloud coverage (%)
    - **strategy**: Merging strategy (best_quality, most_recent, all)
    - **limit**: Maximum number of results
    """
    try:
        results = await registry.search_all(query, strategy, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
async def list_providers():
    """List all registered satellite data providers"""
    return {
        "providers": [
            {
                "name": name,
                "type": type(adapter).__name__
            }
            for name, adapter in registry.adapters.items()
        ]
    }
 