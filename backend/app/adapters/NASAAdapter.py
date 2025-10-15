from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from app.adapters.adapter import SatelliteAPIAdapter
from app.db.models import UnifiedSatelliteImage, SearchQuery, SatelliteInfo

class NASAAdapter(SatelliteAPIAdapter):
    """Adapter for NASA Earth Imagery API"""
    
    BASE_URL = "https://api.nasa.gov/planetary/earth"
    
    def __init__(self, api_key: str = "DEMO_KEY"):
        super().__init__(api_key)
    
    async def search(self, query: SearchQuery) -> List[UnifiedSatelliteImage]:
        """Search NASA Landsat imagery"""
        results = []
        
        # NASA API uses center point, so calculate from bbox
        center_lat = (query.bbox.min_lat + query.bbox.max_lat) / 2
        center_lon = (query.bbox.min_lon + query.bbox.max_lon) / 2
        
        # Query available dates
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/assets",
                params={
                    "lon": center_lon,
                    "lat": center_lat,
                    "begin": query.date_range.start.strftime("%Y-%m-%d"),
                    "end": query.date_range.end.strftime("%Y-%m-%d"),
                    "api_key": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("results", [])[:10]:  # Limit results
                date = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                age_days = (datetime.now() - date).days
                
                unified_image = UnifiedSatelliteImage(
                    id=self.generate_unified_id("nasa", item["id"]),
                    timestamp=date,
                    bbox=query.bbox,
                    satellite=SatelliteInfo(
                        name="Landsat 8",
                        provider="NASA/USGS",
                        sensor_type="OLI"
                    ),
                    bands=self.normalize_bands(["B4", "B3", "B2"]),
                    resolution_meters=30.0,
                    cloud_coverage=None,  # NASA API doesn't provide this
                    source_provider="nasa",
                    source_id=item["id"],
                    source_url=item.get("url", ""),
                    quality_score=self.calculate_quality_score(None, 30.0, age_days)
                )
                results.append(unified_image)
        
        except Exception as e:
            print(f"NASA API error: {e}")
        
        return results
    
    async def get_metadata(self, image_id: str) -> Dict[str, Any]:
        """Get metadata for NASA image"""
        return {"provider": "nasa", "image_id": image_id}
    
    def normalize_bands(self, raw_bands: List[str]) -> List[str]:
        """Map Landsat bands to standard names"""
        band_mapping = {
            "B2": "blue",
            "B3": "green",
            "B4": "red",
            "B5": "nir",
            "B6": "swir1",
            "B7": "swir2"
        }
        return [band_mapping.get(b, b.lower()) for b in raw_bands]