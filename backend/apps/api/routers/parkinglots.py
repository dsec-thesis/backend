from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from backend.apps.api.dependencies import get_user_id
from backend.apps.container import Container
from backend.contexts.parkinglot import application as parkinglot
from backend.contexts.parkinglot.domain import ParkinglotAggregate, ParkinglotRepository
from backend.contexts.shared.domain import EventBus, OwnerId, ParkinglotId

router = APIRouter()


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
@inject
def create_parkinglot(
    command: parkinglot.CreateParkinglotCommand,
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
) -> None:
    return command.handle(owner_id, repo, bus)


@router.get("")
@inject
def list_parkinglots(
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
) -> List[ParkinglotAggregate]:
    return parkinglot.list_parkinglots(owner_id, repo)


@router.get("/{parkinglot_id}")
@inject
def get_parkinglot(
    parkinglot_id: ParkinglotId,
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
):
    return repo.get(parkinglot_id, owner_id)


@router.put("/{parkinglot_id}/price")
@inject
def change_price(
    command: parkinglot.ChangeParkinglotPriceCommand,
    owner_id: OwnerId = Depends(get_user_id),
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
    bus: EventBus = Depends(Provide[Container.eventbus]),
) -> None:
    return command.handle(owner_id, repo, bus)
