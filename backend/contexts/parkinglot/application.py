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


def create_parkinglot(
    parkinglot_id: ParkinglotId,
    name: str,
    street: str,
    coordinates: Coordinates,
    price: Price,
    owner_id: OwnerId,
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if repo.get(parkinglot_id, owner_id):
        return
    parkinglot = ParkinglotAggregate.create(
        parkinglot_id=parkinglot_id,
        owner_id=owner_id,
        name=name,
        street=street,
        coordinates=coordinates,
        price=price,
    )
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())


class AccommodateBookingCommand(BaseModel):
    booking_id: BookingId
    booking_duration: Optional[timedelta]
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


def register_spaces_command(
    parkinglot_id: ParkinglotId,
    space_ids: List[ParkingSpaceId],
    owner_id: OwnerId,
    repo: ParkinglotRepository,
    bus: EventBus,
):
    if not (parkinglot := repo.get(parkinglot_id, owner_id)):
        return None
    parkinglot.register_spaces(space_ids)
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None


def change_parkinglot_price(
    parkinglot_id: ParkinglotId,
    price: Price,
    owner_id: OwnerId,
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if not (parkinglot := repo.get(parkinglot_id, owner_id)):
        return None
    parkinglot.change_price(price)
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


def release_space(
    parkinglot_id: ParkinglotId,
    booking_id: BookingId,
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if not (parkinglot := repo.get(parkinglot_id)):
        return None
    parkinglot.release_space(booking_id)
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None
