from typing import List, Dict, Any
from enum import Enum
import asyncio

from app.adapters.adapter import SatelliteAPIAdapter
from app.db.models import UnifiedSatelliteImage, SearchQuery

class MergeStrategy(str, Enum):
    BEST_QUALITY = "best_quality"
    MOST_RECENT = "most_recent"
    ALL = "all"

class SatelliteAPIRegistry:
    """Manages multiple satellite API adapters and merges results"""
    
    def __init__(self):
        self.adapters: Dict[str, SatelliteAPIAdapter] = {}
    
    def register_adapter(self, name: str, adapter: SatelliteAPIAdapter):
        """Register a new API adapter"""
        self.adapters[name] = adapter
    
    async def search_all(self, query: SearchQuery, 
                        strategy: MergeStrategy = MergeStrategy.BEST_QUALITY,
                        limit: int = 20) -> List[UnifiedSatelliteImage]:
        """Search all registered APIs and merge results"""
        
        # Search all APIs concurrently
        tasks = [adapter.search(query) for adapter in self.adapters.values()]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
        
        # Apply merging strategy
        merged = self._apply_merge_strategy(all_results, strategy)
        
        return merged[:limit]
    
    def _apply_merge_strategy(self, results: List[UnifiedSatelliteImage], 
                             strategy: MergeStrategy) -> List[UnifiedSatelliteImage]:
        """Apply merging strategy to results"""
        
        if strategy == MergeStrategy.ALL:
            # Return all results sorted by quality
            return sorted(results, key=lambda x: x.quality_score, reverse=True)
        
        elif strategy == MergeStrategy.BEST_QUALITY:
            # Group by approximate time (same day) and location
            # Return best quality from each group
            grouped = self._group_similar_images(results)
            return [max(group, key=lambda x: x.quality_score) for group in grouped]
        
        elif strategy == MergeStrategy.MOST_RECENT:
            # Return most recent images
            return sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        return results
    
    def _group_similar_images(self, images: List[UnifiedSatelliteImage]) -> List[List[UnifiedSatelliteImage]]:
        """Group images by similar timestamp (same day)"""
        groups = {}
        for img in images:
            day_key = img.timestamp.date()
            if day_key not in groups:
                groups[day_key] = []
            groups[day_key].append(img)
        return list(groups.values())
    
    async def close_all(self):
        """Close all adapter connections"""
        for adapter in self.adapters.values():
            await adapter.close()