import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key
from pydantic import parse_obj_as

from backend.contexts.parkinglot.domain import ParkinglotAggregate, ParkinglotRepository
from backend.contexts.shared.domain import OwnerId, ParkinglotId


class DynamodbParkinglotRepository(ParkinglotRepository):
    def __init__(self, table_name: str, inverted_index: str) -> None:
        self._inverted_index = inverted_index
        resource = boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def save(self, parkinglot: ParkinglotAggregate) -> None:
        parkinglot.refresh_updated_on()
        item = json.loads(
            parkinglot.json(exclude={"id", "owner_id", "version"}),
            parse_float=Decimal,
        )
        self._table.put_item(
            Item={
                "pk": str(parkinglot.owner_id),
                "sk": f"PARKINGLOT::{parkinglot.id}",
                "version": parkinglot.version + 1,
                **item,
            },
            ConditionExpression=(
                Attr("version").not_exists() | Attr("version").eq(parkinglot.version)
            ),
        )

    def get(
        self,
        parkinglot_id: ParkinglotId,
        owner_id: Optional[OwnerId] = None,
    ) -> Optional[ParkinglotAggregate]:
        owner_id = owner_id or self._resolve_owner(parkinglot_id)
        if not owner_id:
            return None
        item = self._table.get_item(
            Key={"pk": str(owner_id), "sk": f"PARKINGLOT::{parkinglot_id}"}
        ).get("Item")
        return ParkinglotAggregate.parse_obj(self._parse_item(item)) if item else None

    def _format_sk(self, parkinglot_id: ParkinglotId) -> str:
        return f"PARKINGLOT::{parkinglot_id}"

    def _resolve_owner(self, parkinglot_id: ParkinglotId) -> Optional[OwnerId]:
        items = self._table.query(
            IndexName=self._inverted_index,
            KeyConditionExpression=Key("sk").eq(self._format_sk(parkinglot_id)),
        )["Items"]
        if not items:
            return None
        return OwnerId(str(items[0]["pk"]))

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        items = self._table.query(
            KeyConditionExpression=(
                Key("pk").eq(str(owner_id)) & Key("sk").begins_with("PARKINGLOT::")
            ),
        )["Items"]

        return parse_obj_as(
            List[ParkinglotAggregate], (self._parse_item(i) for i in items)
        )

    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        item["owner_id"] = item["pk"]
        item["id"] = str(item["sk"]).split("::")[1]
        return item


class RamParkinglotRepository(ParkinglotRepository):
    def save(self, parkinglot: ParkinglotAggregate) -> None:
        return super().save(parkinglot)

    def get(
        self,
        parkinglot_id: ParkinglotId,
        owner_id: Optional[OwnerId] = None,
    ) -> Optional[ParkinglotAggregate]:
        return super().get(parkinglot_id, owner_id)

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        return super().list(owner_id)
