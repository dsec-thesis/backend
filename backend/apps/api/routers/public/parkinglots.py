from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.apps.api.routers.models import Message
from backend.contexts.parkinglot.domain import ParkinglotRepository

from backend.contexts.shared.domain import ParkinglotId

from dependency_injector.wiring import Provide, inject
from backend.apps.container import Container
from backend.contexts.parkinglot import application as parkinglots

router = APIRouter()


@router.get(
    "/{parkinglot_id}",
    responses={
        status.HTTP_200_OK: {"model": parkinglots.Parkinglot},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@inject
def get_parkinglot(
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
):
    if not (
        parkinglot := parkinglots.get_parkinglot(
            parkinglot_id=parkinglot_id,
            repo=repo,
        )
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="Parkinglot not found").dict(),
        )
    return parkinglot


class ListParkinglotSpacesResponse(BaseModel):
    spaces: List[parkinglots.Space]


@router.get("/{parkinglot_id}/spaces", response_model=ListParkinglotSpacesResponse)
@inject
def get_parkinglot_spaces(
    parkinglot_id: ParkinglotId,
    repo: ParkinglotRepository = Depends(Provide[Container.parkinglot_repository]),
):
    return ListParkinglotSpacesResponse(
        spaces=parkinglots.get_parkinglot_spaces(parkinglot_id=parkinglot_id, repo=repo)
    )
