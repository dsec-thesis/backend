from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.contexts.parkinglot.domain import (
    Coordinates,
    ParkingSpace,
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
        return None
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
    return None


def accomodate_booking(
    booking_id: BookingId,
    parkinglot_id: ParkinglotId,
    driver_id: DriverId,
    booking_duration: Optional[timedelta],
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if not (parkinglot := repo.get(parkinglot_id)):
        return None
    parkinglot.accommodate_booking(
        driver_id=driver_id,
        booking_id=booking_id,
        booking_duration=booking_duration,
    )
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None


def register_concentrator(
    parkinglot_id: ParkinglotId,
    owner_id: OwnerId,
    concentrator_id: str,
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if not (parkinglot := repo.get(parkinglot_id, owner_id)):
        return None
    parkinglot.register_concentrator(concentrator_id)
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


def get_parkinglot_aggregate(
    owner_id: OwnerId,
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository,
) -> Optional[ParkinglotAggregate]:
    return repo.get(parkinglot_id, owner_id)


def list_parkinglot_spaces(
    user_id: UUID,
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository,
) -> List[ParkingSpace]:
    if not (parkinglot := repo.get(parkinglot_id)):
        return []
    if user_id not in (parkinglot.owner_id, parkinglot.concentrator_id):
        return []
    return parkinglot.spaces


class Parkinglot(BaseModel):
    id: ParkinglotId
    name: str
    street: str
    coordinates: Coordinates
    price: Price
    free_spaces: int


def get_parkinglot(
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository,
) -> Optional[Parkinglot]:
    if not (parkinglot := repo.get(parkinglot_id=parkinglot_id)):
        return None
    return Parkinglot(**parkinglot.dict())


class Space(BaseModel):
    id: ParkingSpaceId
    booked: bool
    booked_util: Optional[datetime] = None


def get_parkinglot_spaces(
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository,
) -> List[Space]:
    if not (parkinglot := repo.get(parkinglot_id)):
        return []
    return [
        Space(
            id=s.id,
            booked=bool(s.booked_by),
            booked_util=s.booked_util,
        )
        for s in parkinglot.spaces
    ]


def release_space(
    parkinglot_id: ParkinglotId,
    space_id: ParkingSpaceId,
    repo: ParkinglotRepository,
    bus: EventBus,
) -> None:
    if not (parkinglot := repo.get(parkinglot_id)):
        return None
    parkinglot.release_space(space_id)
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None


def concentrator_take_space(
    parkinglot_id: ParkinglotId,
    space_id: ParkingSpaceId,
    concentrator_id: str,
    repo: ParkinglotRepository,
    bus: EventBus,
):
    if not (parkinglot := repo.get(parkinglot_id)):
        return None
    if concentrator_id != parkinglot.concentrator_id:
        return None
    parkinglot.take_space(space_id)
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None


def concentrator_release_space(
    parkinglot_id: ParkinglotId,
    space_id: ParkingSpaceId,
    concentrator_id: str,
    repo: ParkinglotRepository,
    bus: EventBus,
):
    if not (parkinglot := repo.get(parkinglot_id)):
        return None
    if concentrator_id != parkinglot.concentrator_id:
        return None
    parkinglot.release_space(space_id)
    print(parkinglot)
    repo.save(parkinglot)
    bus.publish(parkinglot.pull_events())
    return None
