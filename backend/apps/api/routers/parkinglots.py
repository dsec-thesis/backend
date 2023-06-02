from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.apps.api.dependencies import (
    create_eventbus,
    create_parkinglot_repository,
    get_user_id,
)
from backend.contexts.parkinglot import application as parkinglot
from backend.contexts.parkinglot.domain import ParkinglotRepository
from backend.contexts.shared.domain import EventBus, OwnerId, ParkinglotId

router = APIRouter()


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def create_parkinglot(
    command: parkinglot.CreateParkinglotCommand,
    owner_id: Annotated[OwnerId, Depends(get_user_id)],
    repo: Annotated[ParkinglotRepository, Depends(create_parkinglot_repository)],
    bus: Annotated[EventBus, Depends(create_eventbus)],
) -> None:
    return command.handle(owner_id, repo, bus)


@router.get("")
def list_parkinglots(
    owner_id: Annotated[OwnerId, Depends(get_user_id)],
    repo: Annotated[ParkinglotRepository, Depends(create_parkinglot_repository)],
):
    return parkinglot.list_parkinglots(owner_id, repo)


@router.get("/{parkinglot_id}")
def get_parkinglot(
    parkinglot_id: ParkinglotId,
    owner_id: Annotated[OwnerId, Depends(get_user_id)],
    repo: Annotated[ParkinglotRepository, Depends(create_parkinglot_repository)],
):
    return repo.get(parkinglot_id, owner_id)


@router.put("/{parkinglot_id}/price")
def change_price(
    command: parkinglot.ChangeParkinglotPriceCommand,
    owner_id: Annotated[OwnerId, Depends(get_user_id)],
    repo: Annotated[ParkinglotRepository, Depends(create_parkinglot_repository)],
    bus: Annotated[EventBus, Depends(create_eventbus)],
) -> None:
    return command.handle(owner_id, repo, bus)
