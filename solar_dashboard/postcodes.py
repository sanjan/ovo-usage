"""
Australian postcode lookup for location data.

Data sourced from Matthew Proctor's Australian Postcodes database:
https://www.matthewproctor.com/australian_postcodes

This free database provides postcode, locality, state, and coordinates
for Australian locations.
"""

import csv
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Location:
    """Australian location with coordinates."""
    postcode: str
    locality: str
    state: str
    latitude: float
    longitude: float
    
    @property
    def display_name(self) -> str:
        return f"{self.locality}, {self.state} {self.postcode}"
    
    def to_dict(self) -> dict:
        return {
            'postcode': self.postcode,
            'locality': self.locality,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'display_name': self.display_name
        }


class PostcodeDatabase:
    """
    Australian postcode database with location lookup.
    
    Data from: https://www.matthewproctor.com/australian_postcodes
    """
    
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            # Default to data directory relative to package
            package_dir = Path(__file__).parent.parent
            data_path = package_dir / 'data' / 'australian_postcodes.csv'
        
        self.data_path = Path(data_path)
        self._locations: dict[str, list[Location]] = {}
        self._loaded = False
    
    def _ensure_loaded(self):
        """Lazy load the postcode data."""
        if self._loaded:
            return
        
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Postcode database not found at {self.data_path}. "
                "Please download from https://www.matthewproctor.com/australian_postcodes"
            )
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                postcode = row.get('postcode', '').strip()
                if not postcode:
                    continue
                
                # Get coordinates, defaulting to 0 if not available
                try:
                    lat = float(row.get('lat', 0) or 0)
                    lon = float(row.get('long', 0) or 0)
                except (ValueError, TypeError):
                    lat, lon = 0.0, 0.0
                
                # Skip entries without valid coordinates
                if lat == 0 and lon == 0:
                    continue
                
                location = Location(
                    postcode=postcode,
                    locality=row.get('locality', '').strip(),
                    state=row.get('state', '').strip(),
                    latitude=lat,
                    longitude=lon
                )
                
                if postcode not in self._locations:
                    self._locations[postcode] = []
                self._locations[postcode].append(location)
        
        self._loaded = True
    
    def lookup(self, postcode: str) -> list[Location]:
        """
        Look up locations by postcode.
        
        Args:
            postcode: Australian postcode (e.g., "3000", "2000")
            
        Returns:
            List of Location objects (postcodes can have multiple localities)
        """
        self._ensure_loaded()
        postcode = str(postcode).strip().zfill(4)
        return self._locations.get(postcode, [])
    
    def get_primary_location(self, postcode: str) -> Optional[Location]:
        """
        Get the primary (first) location for a postcode.
        
        Args:
            postcode: Australian postcode
            
        Returns:
            Location object or None if not found
        """
        locations = self.lookup(postcode)
        return locations[0] if locations else None
    
    def search(self, query: str, limit: int = 20) -> list[Location]:
        """
        Search for locations by postcode or locality name.
        
        Args:
            query: Search string (postcode or suburb name)
            limit: Maximum results to return
            
        Returns:
            List of matching Location objects
        """
        self._ensure_loaded()
        query = query.strip().lower()
        results = []
        
        # First, try exact postcode match
        if query.isdigit():
            postcode = query.zfill(4)
            if postcode in self._locations:
                results.extend(self._locations[postcode])
        
        # Then search by locality name
        for postcode, locations in self._locations.items():
            for loc in locations:
                if query in loc.locality.lower():
                    if loc not in results:
                        results.append(loc)
                        if len(results) >= limit:
                            return results
        
        return results[:limit]
    
    def get_all_postcodes(self) -> list[str]:
        """Get list of all available postcodes."""
        self._ensure_loaded()
        return sorted(self._locations.keys())
    
    def get_states(self) -> list[str]:
        """Get list of all states."""
        return ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']


# Default database instance
_db: Optional[PostcodeDatabase] = None


def get_database() -> PostcodeDatabase:
    """Get the default postcode database instance."""
    global _db
    if _db is None:
        _db = PostcodeDatabase()
    return _db


def lookup_postcode(postcode: str) -> Optional[Location]:
    """
    Quick lookup of a postcode.
    
    Args:
        postcode: Australian postcode
        
    Returns:
        Primary Location for the postcode, or None
    """
    return get_database().get_primary_location(postcode)


def search_locations(query: str, limit: int = 20) -> list[dict]:
    """
    Search for locations and return as dictionaries.
    
    Args:
        query: Search string
        limit: Maximum results
        
    Returns:
        List of location dictionaries
    """
    locations = get_database().search(query, limit)
    return [loc.to_dict() for loc in locations]


# Common major city postcodes for quick reference
MAJOR_CITIES = {
    'sydney': Location('2000', 'Sydney', 'NSW', -33.8688, 151.2093),
    'melbourne': Location('3000', 'Melbourne', 'VIC', -37.8136, 144.9631),
    'brisbane': Location('4000', 'Brisbane', 'QLD', -27.4698, 153.0251),
    'perth': Location('6000', 'Perth', 'WA', -31.9505, 115.8605),
    'adelaide': Location('5000', 'Adelaide', 'SA', -34.9285, 138.6007),
    'hobart': Location('7000', 'Hobart', 'TAS', -42.8821, 147.3272),
    'darwin': Location('0800', 'Darwin', 'NT', -12.4634, 130.8456),
    'canberra': Location('2600', 'Canberra', 'ACT', -35.2809, 149.1300),
}

