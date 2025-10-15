from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import httpx

from app.db.models import UnifiedSatelliteImage, SearchQuery


class SatelliteAPIAdapter(ABC):
    """Base class for all satellite API adapters"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[UnifiedSatelliteImage]:
        """Search for satellite imagery matching the query"""
        pass
    
    @abstractmethod
    async def get_metadata(self, image_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a specific image"""
        pass
    
    @abstractmethod
    def normalize_bands(self, raw_bands: List[str]) -> List[str]:
        """Normalize band names to standard format"""
        pass
    
    def generate_unified_id(self, provider: str, source_id: str) -> str:
        """Generate a unique ID for our unified system"""
        combined = f"{provider}:{source_id}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def calculate_quality_score(self, cloud_coverage: Optional[float], 
                                 resolution: float, age_days: float) -> float:
        """Calculate quality score (0-100) based on multiple factors"""
        score = 100.0
        
        # Cloud coverage penalty (0-40 points)
        if cloud_coverage is not None:
            score -= min(cloud_coverage, 40)
        
        # Resolution penalty (0-30 points)
        # Penalize worse than 10m resolution
        if resolution > 10:
            score -= min((resolution - 10) * 2, 30)
        
        # Age penalty (0-30 points)
        # Penalize images older than 30 days
        if age_days > 30:
            score -= min((age_days - 30) / 10, 30)
        
        return max(0.0, score)
    
    async def close(self):
        await self.client.aclose()
