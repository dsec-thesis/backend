from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Protocol

from pydantic import BaseModel, Field

from backend.contexts.shared.domain import (
    AggregateRoot,
    BookingId,
    DomainEvent,
    DriverId,
    OwnerId,
    ParkinglotId,
    ParkingSpaceId,
)

Price = Decimal


class Coordinate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., gt=-180, le=180)


class Address(BaseModel):
    street: str
    coordinate: Coordinate


class ParkingSpace(BaseModel):
    id: ParkingSpaceId
    booked_by: Optional[DriverId] = None
    booked_from: Optional[datetime] = None
    booked_util: Optional[datetime] = None
    booking_id: Optional[BookingId] = None

    def is_booked(self) -> bool:
        return self.booked_by is not None

    def book(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
        booking_duration: timedelta,
    ) -> None:
        self.booked_by = driver_id
        self.booking_id = booking_id
        self.booked_from = datetime.now()
        self.booked_util = self.booked_from + booking_duration


class ParkinglotAggregate(AggregateRoot[ParkinglotId]):
    owner_id: OwnerId
    name: str
    address: Address
    price: Price
    free_spaces: int = 0
    spaces: List[ParkingSpace] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        parkinglot_id: ParkinglotId,
        owner_id: OwnerId,
        name: str,
        address: Address,
        price: Price,
    ) -> "ParkinglotAggregate":
        parkinglot = cls(
            id=parkinglot_id,
            owner_id=owner_id,
            name=name,
            address=address,
            price=price,
        )
        parkinglot.push_event(
            ParkinglotCreated(
                aggregate_id=parkinglot.id,
                owner_id=parkinglot.owner_id,
                name=parkinglot.name,
                address=parkinglot.address,
            )
        )
        return parkinglot

    def change_price(self, price: Price) -> None:
        self.price = price

    def find_free_space(self) -> Optional[ParkingSpace]:
        return next((s for s in self.spaces if s.booking_id is None), None)

    def accommodate_booking(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
        booking_duration: timedelta,
    ) -> Optional[Price]:
        if not self.free_spaces:
            return None
        if not (free_space := self.find_free_space()):
            return None
        free_space.book(driver_id, booking_id, booking_duration)
        self.free_spaces -= 1
        return self.price * Decimal(booking_duration.total_seconds())

    def register_spaces(self, space_ids: List[ParkingSpaceId]) -> None:
        spaces = [ParkingSpace(id=space_id) for space_id in space_ids]
        self.spaces.extend(spaces)
        for space in spaces:
            self.push_event(
                ParkingSpaceCreated(aggregate_id=self.id, space_id=space.id)
            )


class ParkinglotCreated(DomainEvent[ParkinglotId]):
    owner_id: OwnerId
    name: str
    address: Address


class BookingAccommodated(DomainEvent[ParkinglotId]):
    price: Price


class ParkingSpaceCreated(DomainEvent[ParkinglotId]):
    space_id: ParkingSpaceId


class ParkinglotRepository(Protocol):
    def save(self, parkinglot: ParkinglotAggregate) -> None:
        ...

    def get(
        self,
        parkinglot_id: ParkinglotId,
        owner_id: Optional[OwnerId] = None,
    ) -> Optional[ParkinglotAggregate]:
        ...

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        ...