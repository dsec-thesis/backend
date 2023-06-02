from datetime import timedelta
from typing import List, Optional

from pydantic import BaseModel

from backend.contexts.parkinglot.domain import (
    Coordinates,
    ParkinglotAggregate,
    ParkinglotRepository,
    Price,
)
from backend.contexts.shared.domain import (
    BookingId,
    DriverId,
    EventBus,
    OwnerId,
    ParkinglotId,
    ParkingSpaceId,
)


class CreateParkinglotCommand(BaseModel):
    parkinglot_id: ParkinglotId
    name: str
    street: str
    coordinates: Coordinates
    price: Price

    def handle(
        self,
        owner_id: OwnerId,
        repo: ParkinglotRepository,
        bus: EventBus,
    ) -> None:
        parkinglot = ParkinglotAggregate.create(
            parkinglot_id=self.parkinglot_id,
            owner_id=owner_id,
            name=self.name,
            street=self.street,
            coordinates=self.coordinates,
            price=self.price,
        )
        repo.save(parkinglot)
        bus.publish(parkinglot.pull_events())


class RegisterSpacesCommand(BaseModel):
    parkinglot_id: ParkinglotId
    space_ids: List[ParkingSpaceId]

    def handle(
        self,
        owner_id: OwnerId,
        repo: ParkinglotRepository,
        bus: EventBus,
    ) -> None:
        if not (parkinglot := repo.get(self.parkinglot_id, owner_id)):
            return None
        parkinglot.register_spaces(self.space_ids)
        repo.save(parkinglot)
        bus.publish(parkinglot.pull_events())
        return None


class ChangeParkinglotPriceCommand(BaseModel):
    parkinglot_id: ParkinglotId
    price: Price

    def handle(
        self,
        owner_id: OwnerId,
        repo: ParkinglotRepository,
        bus: EventBus,
    ) -> None:
        if not (parkinglot := repo.get(self.parkinglot_id, owner_id)):
            return None
        parkinglot.change_price(self.price)
        repo.save(parkinglot)
        bus.publish(parkinglot.pull_events())
        return None


class AccommodateBookingCommand(BaseModel):
    booking_id: BookingId
    booking_duration: timedelta
    parkinglot_id: ParkinglotId

    def handle(
        self,
        driver_id: DriverId,
        repo: ParkinglotRepository,
        bus: EventBus,
    ) -> None:
        if not (parkinglot := repo.get(self.parkinglot_id)):
            return None
        parkinglot.accommodate_booking(
            driver_id,
            self.booking_id,
            self.booking_duration,
        )
        repo.save(parkinglot)
        bus.publish(parkinglot.pull_events())
        return None


def list_parkinglots(
    owner_id: OwnerId,
    repo: ParkinglotRepository,
) -> List[ParkinglotAggregate]:
    return repo.list(owner_id)


def get_parkinglot(
    owner_id: OwnerId,
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository,
) -> Optional[ParkinglotAggregate]:
    return repo.get(parkinglot_id, owner_id)
