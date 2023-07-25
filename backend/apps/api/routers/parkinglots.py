from decimal import Decimal
from typing import Annotated, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from backend.apps.api.dependencies import get_user_id
from backend.apps.api.routers.models import (
    CreateParkinglotRequest,
    ListParkinglotsResponse,
    Message,
)
from backend.apps.container import Container
from backend.contexts.parkinglot import application as parkinglots
from backend.contexts.parkinglot.domain import ParkinglotAggregate, ParkinglotRepository
from backend.contexts.shared.domain import (
    EventBus,
    OwnerId,
    ParkingSpaceId,
    ParkinglotId,
)

router = APIRouter()


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
@inject
def create_parkinglot(
    data: CreateParkinglotRequest,
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
):
    return parkinglots.create_parkinglot(
        parkinglot_id=data.parkinglot_id,
        name=data.name,
        street=data.street,
        coordinates=data.coordinates,
        price=data.price,
        owner_id=owner_id,
        repo=repo,
        bus=bus,
    )


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": ListParkinglotsResponse},
    },
)
@inject
def list_parkinglots(
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
):
    return ListParkinglotsResponse(
        parkinglots=parkinglots.list_parkinglots(owner_id, repo)
    )


@router.get(
    "/{parkinglot_id}",
    responses={
        status.HTTP_200_OK: {"model": ParkinglotAggregate},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@inject
def get_parkinglot(
    parkinglot_id: ParkinglotId,
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
):
    if not (parkinglot := repo.get(parkinglot_id, owner_id)):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="Parkinglot not found"),
        )
    return parkinglot


@router.put("/{parkinglot_id}/price", status_code=status.HTTP_204_NO_CONTENT)
@inject
def change_price(
    parkinglot_id: ParkinglotId,
    price: Annotated[Decimal, Body(embed=True)],
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
):
    return parkinglots.change_parkinglot_price(
        parkinglot_id=parkinglot_id,
        price=price,
        owner_id=owner_id,
        repo=repo,
        bus=bus,
    )


@router.put("/{parkinglot_id}/spaces", status_code=status.HTTP_204_NO_CONTENT)
@inject
def register_spaces(
    parkinglot_id: ParkinglotId,
    space_ids: Annotated[List[ParkingSpaceId], Body(embed=True)],
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
) -> None:
    return parkinglots.register_spaces_command(
        parkinglot_id=parkinglot_id,
        space_ids=space_ids,
        owner_id=owner_id,
        repo=repo,
        bus=bus,
    )
