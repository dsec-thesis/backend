from datetime import timedelta
from typing import List, Optional

from pydantic import BaseModel

from backend.contexts.booking.domain import BookingAggregate
from backend.contexts.parkinglot.domain import Coordinates, ParkinglotAggregate, Price
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


class CreateParkinglotRequest(BaseModel):
    parkinglot_id: ParkinglotId
    name: str
    street: str
    coordinates: Coordinates
    price: Price


class ListParkinglotsResponse(BaseModel):
    parkinglots: List[ParkinglotAggregate]
