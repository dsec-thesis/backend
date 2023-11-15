from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.apps.container import Container
from backend.contexts.searcher import application as searcher
from backend.contexts.searcher.domain import ParkinglotSearchRepository
from dependency_injector.wiring import Provide, inject

router = APIRouter()


@router.get("")
@inject
def search(
    repo: ParkinglotSearchRepository = Depends(
        Provide[Container.parkinglot_search_repository]
    ),
    lat: Annotated[Optional[float], Query(ge=-90, le=90)] = None,
    lng: Annotated[Optional[float], Query(gt=-180, le=180)] = None,
    central_cell: Annotated[Optional[str], Query()] = None,
    start_distance: Annotated[int, Query(ge=0)] = 0,
    end_distance: Annotated[int, Query(ge=0)] = 10,
    limit: Annotated[int, Query()] = 10,
) -> searcher.SearchResponse:
    if central_cell:
        return searcher.search_by_cell(
            central_cell=central_cell,
            start_distance=start_distance,
            end_distance=end_distance,
            limit=limit,
            repo=repo,
        )

    if lat and lng:
        return searcher.search_by_coordinates(
            lat=lat,
            lng=lng,
            start_distance=start_distance,
            end_distance=end_distance,
            limit=limit,
            repo=repo,
        )

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="lat and lng or cell must not be null",
    )
