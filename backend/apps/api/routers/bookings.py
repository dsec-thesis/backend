from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from backend.apps.api.dependencies import (
    get_user_id,
)
from backend.apps.container import Container
from backend.contexts.booking import application as bookings
from backend.contexts.booking.application import BookingRepository
from backend.contexts.booking.domain import BookingAggregate
from backend.contexts.shared.domain import BookingId, DriverId, EventBus

router = APIRouter()


@router.put("")
@inject
def create_booking(
    command: bookings.CreateBookingCommand,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
) -> None:
    return command.handle(driver_id, repo, bus)


@router.get("")
@inject
def list_bookings(
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
) -> List[BookingAggregate]:
    return bookings.list_bookings(driver_id, repo)


@router.get("/{booking_id}")
@inject
def get_booking(
    booking_id: BookingId,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
) -> BookingAggregate:
    if not (booking := bookings.get_booking(driver_id, booking_id, repo)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    return booking


@router.delete("/{booking_id}")
@inject
def cancel_booking(
    booking_id: BookingId,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
) -> None:
    return bookings.cancel_booking_by_driver(
        booking_id=booking_id,
        driver_id=driver_id,
        repo=repo,
        bus=bus,
    )
