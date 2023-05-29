from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key
from pydantic import parse_obj_as


from backend.contexts.parkinglot.domain import ParkinglotAggregate, ParkinglotRepository
from backend.contexts.shared.domain import OwnerId, ParkinglotId


class DynamodbParkinglotRepository(ParkinglotRepository):
    def __init__(self, table_name: str) -> None:
        resource = boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def save(self, parkinglot: ParkinglotAggregate) -> None:
        data = parkinglot.dict(exclude={"id", "owner_id", "version"})
        self._table.put_item(
            Item={
                "pk": str(parkinglot.owner_id),
                "sk": f"PARKINGLOT::{parkinglot.id}",
                "version": parkinglot.version + 1,
                **data,
            },
            ConditionExpression=(
                Attr("version").not_exists() | Attr("version").eq(parkinglot.version)
            ),
        )

    def get(
        self,
        owner_id: OwnerId,
        parkinglot_id: ParkinglotId,
    ) -> Optional[ParkinglotAggregate]:
        item = self._table.get_item(
            Key={
                "pk": str(owner_id),
                "sk": f"PARKINGLOT::{parkinglot_id}",
            }
        )["Item"]

        return ParkinglotAggregate.parse_obj(item) if item else None

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        items = self._table.query(
            KeyConditionExpression=(
                Key("pk").eq(str(owner_id)) & Key("sk").begins_with("PARKINGLOT::")
            ),
        )["Items"]

        return parse_obj_as(List[ParkinglotAggregate], items)


class RamParkinglotRepository(ParkinglotRepository):
    def save(self, parkinglot: ParkinglotAggregate) -> None:
        return super().save(parkinglot)

    def get(
        self,
        owner_id: OwnerId,
        parkinglot_id: ParkinglotId,
    ) -> Optional[ParkinglotAggregate]:
        return super().get(parkinglot_id, owner_id)

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        return super().list(owner_id)
