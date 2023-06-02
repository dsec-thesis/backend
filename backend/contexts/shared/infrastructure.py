import boto3
from backend.contexts.shared.domain import DomainEvent, EventBus


from typing import List


class RamEventBus(EventBus):
    def __init__(self) -> None:
        self.events: List[DomainEvent] = []

    def publish(self, events: List[DomainEvent]) -> None:
        self.events.extend(events)


class SnsEventBus(EventBus):
    def __init__(self, topic_arn: str) -> None:
        self._topic_arn = topic_arn
        self._client = boto3.client("sns")

    def publish(self, events: List[DomainEvent]) -> None:
        self._client.publish_batch(
            TopicArn=self._topic_arn,
            PublishBatchRequestEntries=[
                {
                    "Id": str(e.id),
                    "Message": e.json(),
                    "MessageAttributes": {
                        "name": {
                            "DataType": "String",
                            "StringValue": e.event_name,
                        },
                        "aggregate_id": {
                            "DataType": "String",
                            "StringValue": str(e.aggregate_id),
                        },
                    },
                }
                for e in events
            ],
        )
