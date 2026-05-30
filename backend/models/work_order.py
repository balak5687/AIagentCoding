from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date, time, timezone
from enum import Enum


class DeliveryStatus(str, Enum):
    """Enum for work order delivery status"""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    DELAYED = "delayed"
    CRITICAL = "critical"
    COMPLETED = "completed"


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkOrder(TimestampMixin):
    """
    Work Order model for vehicle service management.
    Tracks job priority, scheduling, delivery status, and service details.
    """
    # Core identification
    id: Optional[str] = Field(None, description="Unique work order identifier")
    
    # Priority and scheduling
    priority: int = Field(
        ..., 
        ge=1, 
        le=5, 
        description="Priority level (1=highest, 5=lowest)"
    )
    due_date: date = Field(
        ..., 
        description="Expected completion date"
    )
    
    # Delivery tracking
    delivery_status: DeliveryStatus = Field(
        default=DeliveryStatus.ON_TRACK,
        description="Current delivery status"
    )
    delay_reason: Optional[str] = Field(
        None, 
        max_length=500,
        description="Reason for delay if applicable"
    )
    delay_duration: Optional[int] = Field(
        None, 
        ge=0,
        description="Delay duration in hours"
    )
    
    # Customer commitments
    promised_delivery_date: Optional[date] = Field(
        None,
        description="Date promised to customer"
    )
    promised_delivery_time: Optional[time] = Field(
        None,
        description="Time promised to customer"
    )
    
    # Service details
    service_advisor_notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Service advisor notes and observations"
    )
    recommendations: Optional[str] = Field(
        None,
        max_length=2000,
        description="Recommended additional services"
    )
    service_type_category: str = Field(
        ...,
        max_length=100,
        description="Category of service (e.g., maintenance, repair, inspection)"
    )
    
    @model_validator(mode='after')
    def validate_delay_fields(self):
        """
        Validate that delay fields are consistent with delivery status.
        If delay_reason or delay_duration is provided, status must be DELAYED or CRITICAL.
        """
        delay_statuses = {DeliveryStatus.DELAYED, DeliveryStatus.CRITICAL}
        has_delay_info = self.delay_reason is not None or self.delay_duration is not None
        is_delayed = self.delivery_status in delay_statuses
        
        if has_delay_info and not is_delayed:
            raise ValueError(
                f"delay_reason or delay_duration provided but status is {self.delivery_status}. "
                f"Status must be DELAYED or CRITICAL when delay information is present."
            )
        
        return self
    
    @field_validator('promised_delivery_date')
    @classmethod
    def validate_promised_date(cls, v, info):
        """Ensure promised delivery date is not in the past"""
        if v and v < datetime.now(timezone.utc).date():
            raise ValueError("promised_delivery_date cannot be in the past")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "priority": 1,
                "due_date": "2026-05-30",
                "delivery_status": "on_track",
                "service_type_category": "major_repair",
                "promised_delivery_date": "2026-05-30",
                "promised_delivery_time": "17:00:00",
                "service_advisor_notes": "Customer reported unusual engine noise",
                "recommendations": "Consider brake inspection due to high mileage"
            }
        }