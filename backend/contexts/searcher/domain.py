from typing import List, Protocol
from pydantic import BaseModel
from backend.contexts.parkinglot.domain import Coordinates

from backend.contexts.shared.domain import ParkinglotId


class Parkinglot(BaseModel):
    h3cell: str
    parkinglot_id: ParkinglotId
    name: str
    street: str
    coordinates: Coordinates


class ParkinglotSearchRepository(Protocol):
    def query(self, h3hashes: List[str]) -> List[Parkinglot]:
        ...
