from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.apps.api.dependencies import (
    get_user_id,
)
from backend.apps.api.routers.models import (
    CreateBookingRequest,
    ListBookingResponse,
    Message,
)
from backend.apps.container import Container
from backend.contexts.booking import application as bookings
from backend.contexts.booking.application import BookingRepository
from backend.contexts.booking.domain import BookingAggregate
from backend.contexts.shared.domain import BookingId, DriverId, EventBus

router = APIRouter()


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
@inject
def create_booking(
    data: CreateBookingRequest,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
):
    return bookings.create_booking(
        booking_id=data.booking_id,
        parkinglot_id=data.parkinglot_id,
        description=data.description,
        duration=data.duration,
        driver_id=driver_id,
        repo=repo,
        bus=bus,
    )


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": ListBookingResponse},
    },
)
@inject
def list_bookings(
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
):
    return ListBookingResponse(bookings=bookings.list_bookings(driver_id, repo))


@router.get(
    "/{booking_id}",
    responses={
        status.HTTP_200_OK: {"model": BookingAggregate},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@inject
def get_booking(
    booking_id: BookingId,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
):
    if not (booking := bookings.get_booking(driver_id, booking_id, repo)):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="Booking not found"),
        )
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def cancel_booking(
    booking_id: BookingId,
    driver_id: DriverId = Depends(get_user_id),
    repo: BookingRepository = Depends(Provide[Container.booking_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
):
    return bookings.cancel_booking_by_driver(
        booking_id=booking_id,
        driver_id=driver_id,
        repo=repo,
        bus=bus,
    )
