import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from backend.apps.api.config import Env, Settings
from backend.contexts.booking.application import BookingRepository
from backend.contexts.booking.infrastructure import (
    DynamodbBookingRepository,
    RamBookingRepository,
)
from backend.contexts.shared.domain import EventBus
from backend.contexts.shared.infrastructure import RamEventBus, SnsEventBus


@lru_cache()
def get_settings():
    return Settings()


@lru_cache()
def create_booking_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> BookingRepository:
    if settings.dynamo_table:
        return DynamodbBookingRepository(settings.dynamo_table)
    return RamBookingRepository()


@lru_cache()
def create_eventbus(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EventBus:
    if settings.sns_topic_arn:
        return SnsEventBus(settings.sns_topic_arn)
        # return SnsEventBus("arn:aws:sns:us-east-1:120429448709:smartparking-dev")
    return RamEventBus()


def get_user_id(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> uuid.UUID:
    if settings.env == Env.AWS_LAMBDA_MAGNUM:
        print(request.scope)
        return uuid.UUID(
            request.scope["aws.event"]["requestContext"]["authorizer"]["jwt"]["claims"][
                "sub"
            ]
        )

    if user_id := settings.test_user_id:
        return user_id

    return uuid.uuid4()