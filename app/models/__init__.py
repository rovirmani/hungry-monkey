from __future__ import annotations
from pydantic import BaseModel

# First import base models
from ..models import (
    Coordinates,
    Location,
    Category,
    OperatingHours,
    Restaurant,
    RestaurantWithHours,
    SearchParams
)

# Then import VAPI models
from .vapi import (
    PhoneNumber,
    Customer,
    Assistant,
    Squad,
    Cost,
    Message,
    VAPICallRequest,
    VAPICallResponse,
    BusinessHoursResponse,
    CallAnalysisResponse
)

# Re-export all models
__all__ = [
    'Coordinates', 'Location', 'Category', 'OperatingHours',
    'Restaurant', 'RestaurantWithHours', 'SearchParams',
    'PhoneNumber', 'Customer', 'Assistant', 'Squad',
    'Cost', 'Message', 'VAPICallRequest', 'VAPICallResponse',
    'BusinessHoursResponse', 'CallAnalysisResponse'
]
