from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.apps.api.dependencies import (
    create_booking_repository,
    create_eventbus,
    get_user_id,
)
from backend.contexts.booking import application as bookings
from backend.contexts.booking.application import Booking, BookingRepository
from backend.contexts.shared.domain import BookingId, DriverId, EventBus, ParkinglotId

router = APIRouter()


@router.put("")
def create_booking(
    booking_id: BookingId,
    parkinglot_id: ParkinglotId,
    driver_id: Annotated[DriverId, Depends(get_user_id)],
    repo: Annotated[BookingRepository, Depends(create_booking_repository)],
    bus: Annotated[EventBus, Depends(create_eventbus)],
) -> None:
    return bookings.create_booking(booking_id, parkinglot_id, driver_id, repo, bus)


@router.get("")
def list_bookings(
    driver_id: Annotated[DriverId, Depends(get_user_id)],
    repo: Annotated[BookingRepository, Depends(create_booking_repository)],
) -> List[Booking]:
    return bookings.list_bookings(driver_id, repo)


@router.get("/{booking_id}")
def get_booking(
    booking_id: BookingId,
    driver_id: Annotated[DriverId, Depends(get_user_id)],
    repo: Annotated[BookingRepository, Depends(create_booking_repository)],
) -> Booking:
    if not (booking := bookings.get_booking(driver_id, booking_id, repo)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking
