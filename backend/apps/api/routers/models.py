from datetime import timedelta
from typing import List, Optional

from pydantic import BaseModel

from backend.contexts.booking.domain import BookingAggregate
from backend.contexts.shared.domain import BookingId, ParkinglotId


class Message(BaseModel):
    message: str


class CreateBookingRequest(BaseModel):
    booking_id: BookingId
    parkinglot_id: ParkinglotId
    description: str
    duration: Optional[timedelta] = None


class ListBookingResponse(BaseModel):
    bookings: List[BookingAggregate]
