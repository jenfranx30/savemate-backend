"""
Common embedded models used across documents
"""
from pydantic import BaseModel, field_validator
from typing import List


class Location(BaseModel):
    """
    GeoJSON Point for geospatial queries
    MongoDB requires [longitude, latitude] order
    """
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]
    
    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        """Validate longitude and latitude ranges"""
        if len(v) != 2:
            raise ValueError('Coordinates must be [longitude, latitude]')
        
        lng, lat = v
        
        if not (-180 <= lng <= 180):
            raise ValueError(f'Longitude must be between -180 and 180, got {lng}')
        
        if not (-90 <= lat <= 90):
            raise ValueError(f'Latitude must be between -90 and 90, got {lat}')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "Point",
                "coordinates": [21.0122, 52.2297]  # Warsaw coordinates
            }
        }


class Address(BaseModel):
    """Physical address"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Poland"
    
    class Config:
        json_schema_extra = {
            "example": {
                "street": "ul. Marszałkowska 123",
                "city": "Warsaw",
                "state": "Mazovia",
                "zip_code": "00-001",
                "country": "Poland"
            }
        }