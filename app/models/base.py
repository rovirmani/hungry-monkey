from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

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

class OperatingHours(BaseModel):
    time_open: Optional[str] = None
    time_closed: Optional[str] = None
    is_hours_verified: bool = False
    is_consenting: bool = False
    is_open: Optional[bool] = None

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
    is_closed: Optional[bool] = None
    is_open: bool = True

    class Config:
        populate_by_name = True

class RestaurantWithHours(Restaurant):
    operating_hours: Optional[OperatingHours] = None

class SearchParams(BaseModel):
    term: Optional[str] = None
    location: str
    radius: Optional[float] = None  # in meters
    limit: Optional[int] = 20  # default to 20 results
    sort_by: Optional[str] = "best_match"  # "best_match", "rating", "review_count", "distance"
    price: Optional[str] = None  # "1,2,3,4"
    categories: Optional[str] = None
    offset: Optional[int] = None
    open_now: Optional[bool] = None

# Import any external schemas here
# from app.models.vapi import VAPICallRequest, VAPICallResponse  # example

# Update forward refs for all models that reference other models
Coordinates.update_forward_refs()
Location.update_forward_refs()
Category.update_forward_refs()
OperatingHours.update_forward_refs()
Restaurant.update_forward_refs()
RestaurantWithHours.update_forward_refs()
SearchParams.update_forward_refs()
