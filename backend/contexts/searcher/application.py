from typing import List

import h3
from pydantic import BaseModel

from backend.contexts.searcher.domain import Parkinglot, ParkinglotSearchRepository


class SearchResponse(BaseModel):
    central_cell: str
    current_distance: int
    parkinglots: List[Parkinglot]


def search_by_coordinates(
    lat: float,
    lng: float,
    start_distance: int,
    end_distance: int,
    limit: int,
    repo: ParkinglotSearchRepository,
) -> SearchResponse:
    return search_by_cell(
        central_cell=h3.latlng_to_cell(lat, lng, 8),
        start_distance=start_distance,
        end_distance=end_distance,
        limit=limit,
        repo=repo,
    )


def search_by_cell(
    central_cell: str,
    start_distance: int,
    end_distance: int,
    limit: int,
    repo: ParkinglotSearchRepository,
) -> SearchResponse:
    current_distance = start_distance - 1
    parkinglots = []
    while len(parkinglots) < limit:
        current_distance += 1
        cells = (
            [central_cell]
            if current_distance == 0
            else h3.grid_ring(central_cell, current_distance)
        )
        parkinglots.extend(repo.query(cells))
        if current_distance >= end_distance:
            break

    return SearchResponse(
        central_cell=central_cell,
        current_distance=current_distance,
        parkinglots=parkinglots,
    )
