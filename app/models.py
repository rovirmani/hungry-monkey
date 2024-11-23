from typing import List, Optional
from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: Optional[str] = "US"
    display_address: Optional[List[str]] = None

class Category(BaseModel):
    alias: str
    title: str

class Restaurant(BaseModel):
    business_id: str = Field(..., alias="id")
    name: str
    rating: float
    price: Optional[str] = None
    phone: Optional[str] = None
    location: Location
    coordinates: Coordinates
    photos: List[str] = []
    categories: List[Category] = []
    is_open: bool = True

    class Config:
        populate_by_name = True

class SearchParams(BaseModel):
    term: Optional[str] = None
    location: str
    radius: Optional[float] = None  # in meters
    limit: Optional[int] = 20
    sort_by: Optional[str] = "best_match"  # "best_match", "rating", "review_count", "distance"
    price: Optional[str] = None  # "1,2,3,4"
    open_now: Optional[bool] = None
