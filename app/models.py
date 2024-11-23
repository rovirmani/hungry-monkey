from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    display_address: Optional[List[str]] = None

class Category(BaseModel):
    alias: str
    title: str

class BusinessHours(BaseModel):
    is_overnight: bool
    start: str  # HH:MM format
    end: str    # HH:MM format
    day: int    # 0-6 (Monday-Sunday)

class Hours(BaseModel):
    hours_type: str
    open: List[BusinessHours]
    is_open_now: bool

class User(BaseModel):
    image_url: Optional[str] = None
    name: str

class Review(BaseModel):
    id: Optional[str] = None
    url: str
    text: str
    rating: float
    user: User
    time_created: Optional[datetime] = None

class Restaurant(BaseModel):
    id: str
    alias: Optional[str] = None
    name: str
    image_url: str
    url: str
    review_count: int
    categories: List[Category]
    rating: float
    coordinates: Coordinates
    price: Optional[str] = None
    location: Optional[Location] = None
    phone: Optional[str] = None
    photos: Optional[List[str]] = None
    hours: Optional[List[Hours]] = None

class SearchParams(BaseModel):
    term: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None  # meters
    categories: Optional[str] = None
    locale: Optional[str] = None
    price: Optional[str] = None  # Comma delimited list of: 1, 2, 3, 4
    open_now: Optional[bool] = None
    open_at: Optional[int] = None
    sort_by: Optional[str] = "best_match"  # best_match, rating, review_count or distance
    limit: Optional[int] = 20
    offset: Optional[int] = None

class AutocompleteParams(BaseModel):
    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    locale: Optional[str] = None
