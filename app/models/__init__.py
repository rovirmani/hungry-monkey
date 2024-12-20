from __future__ import annotations

# Import everything from base.py
from .base import (
    Coordinates,
    Location,
    Category,
    OperatingHours,
    Restaurant,
    RestaurantWithHours,
    SearchParams
)

# Import everything from vapi.py
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
    # Restaurant models
    'Coordinates', 'Location', 'Category', 'OperatingHours',
    'Restaurant', 'RestaurantWithHours', 'SearchParams',
    
    # VAPI models
    'PhoneNumber', 'Customer', 'Assistant', 'Squad', 'Cost',
    'Message', 'VAPICallRequest', 'VAPICallResponse',
    'BusinessHoursResponse', 'CallAnalysisResponse'
]
