from typing import Any, Dict, List

import boto3
from pydantic import parse_obj_as
from backend.contexts.searcher.domain import Parkinglot, ParkinglotSearchRepository
from boto3.dynamodb.conditions import Key


class DynamodbParkinglotSearchRepository(ParkinglotSearchRepository):
    def __init__(self, table_name: str, index_name: str) -> None:
        self._index_name = index_name
        resource = boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def query(self, h3cells: List[str]) -> List[Parkinglot]:
        parkinglots: List[Parkinglot] = []
        for h3cell in h3cells:
            items = self._table.query(
                IndexName=self._index_name,
                KeyConditionExpression=Key("h3cell").eq(h3cell),
            )["Items"]
            parkinglots.extend(
                parse_obj_as(List[Parkinglot], (self._format_item(i) for i in items))
            )
        return parkinglots

    def _format_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        item["parkinglot_id"] = str(item["sk"]).split("::")[1]
        return item


class RamParkinglotSearchRepository(ParkinglotSearchRepository):
    def query(self, h3hashes: List[str]) -> List[Parkinglot]:
        return super().query(h3hashes)
