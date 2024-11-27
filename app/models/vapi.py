from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Union, Literal, Any
from datetime import datetime

class PhoneNumber(BaseModel):
    """Phone number configuration for VAPI calls"""
    # Add phone number fields as needed
    pass

class Customer(BaseModel):
    """Customer information for VAPI calls"""
    # Add customer fields as needed
    pass

class Assistant(BaseModel):
    """Assistant configuration for VAPI calls"""
    # Add assistant fields as needed
    pass

class Squad(BaseModel):
    """Squad configuration for VAPI calls"""
    # Add squad fields as needed
    pass

class Cost(BaseModel):
    """Cost information for a call component"""
    amount: float
    description: str

class Message(BaseModel):
    """Message in a call"""
    # Add message fields as needed
    pass

class VAPICallRequest(BaseModel):
    """Request model for VAPI calls"""
    name: Optional[str] = Field(None, max_length=40, description="Name of the call for reference")
    assistantId: Optional[str] = Field(None, description="ID of existing assistant")
    assistant: Optional[Assistant] = Field(None, description="Transient assistant configuration")
    assistantOverrides: Optional[Dict] = Field(None, description="Assistant setting overrides")
    squadId: Optional[str] = Field(None, description="ID of existing squad")
    squad: Optional[Squad] = Field(None, description="Transient squad configuration")
    phoneNumberId: Optional[str] = Field(None, description="ID of existing phone number")
    phoneNumber: Optional[PhoneNumber] = Field(None, description="Transient phone number configuration")
    customerId: Optional[str] = Field(None, description="ID of existing customer")
    customer: Optional[Customer] = Field(None, description="Transient customer configuration")

    @validator('assistant')
    def validate_assistant(cls, v, values):
        if v is not None and values.get('assistantId') is not None:
            raise ValueError("Cannot specify both assistant and assistantId")
        return v

    @validator('squad')
    def validate_squad(cls, v, values):
        if v is not None and values.get('squadId') is not None:
            raise ValueError("Cannot specify both squad and squadId")
        return v

    @validator('phoneNumber')
    def validate_phone_number(cls, v, values):
        if v is not None and values.get('phoneNumberId') is not None:
            raise ValueError("Cannot specify both phoneNumber and phoneNumberId")
        return v

    @validator('customer')
    def validate_customer(cls, v, values):
        if v is not None and values.get('customerId') is not None:
            raise ValueError("Cannot specify both customer and customerId")
        return v

class VAPICallResponse(BaseModel):
    """Response model for VAPI calls"""
    id: str = Field(..., description="Unique identifier for the call")
    orgId: str = Field(..., description="Org identifier")
    createdAt: datetime = Field(..., description="Creation timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    type: Optional[Literal["inboundPhoneCall", "outboundPhoneCall", "webCall"]] = Field(None)
    costs: Optional[List[Cost]] = Field(None, description="Component costs in USD")
    messages: Optional[List[Message]] = Field(None)
    phoneCallProvider: Optional[Literal["twilio", "vonage", "vapi"]] = Field(None)
    phoneCallTransport: Optional[Literal["sip", "pstn"]] = Field(None)
    status: Optional[Literal["queued", "ringing", "in-progress", "forwarding", "ended"]] = Field(None)
    endedReason: Optional[str] = Field(None)
    startedAt: Optional[datetime] = Field(None)
    endedAt: Optional[datetime] = Field(None)
    cost: Optional[float] = Field(None, description="Total cost in USD")
    costBreakdown: Optional[Dict] = Field(None)
    phoneCallProviderId: Optional[str] = Field(None)
    
    # Include other fields from the response as needed

class BusinessHoursResponse(BaseModel):
    """Response model for business hours check."""
    time_open: str
    time_closed: str  # Fixed the typo in 'closed'
    withdrawing_consent: bool
    is_correct_restaraunt: bool  # Keeping the original spelling from the API

class CallAnalysisResponse(BaseModel):
    """Response model for call analysis."""
    success: bool
    data: BusinessHoursResponse

# Import any external schemas here if needed
# from app.models.base import SomeModel

# Update forward refs for all models that reference other models
PhoneNumber.update_forward_refs()
Customer.update_forward_refs()
Assistant.update_forward_refs()
Squad.update_forward_refs()
Cost.update_forward_refs()
Message.update_forward_refs()
VAPICallRequest.update_forward_refs()
VAPICallResponse.update_forward_refs()
BusinessHoursResponse.update_forward_refs()
CallAnalysisResponse.update_forward_refs()
