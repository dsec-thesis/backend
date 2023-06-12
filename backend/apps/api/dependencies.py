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
from backend.contexts.parkinglot.domain import ParkinglotRepository
from backend.contexts.parkinglot.infrastructure import (
    DynamodbParkinglotRepository,
    RamParkinglotRepository,
)
from backend.contexts.searcher.domain import ParkinglotSearchRepository
from backend.contexts.searcher.infraestructure import (
    DynamodbParkinglotSearchRepository,
    RamParkinglotSearchRepository,
)
from backend.contexts.shared.domain import EventBus
from backend.contexts.shared.infrastructure import RamEventBus, SnsEventBus


@lru_cache()
def get_settings():
    return Settings()


def get_user_id(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> uuid.UUID:
    if settings.env == Env.AWS_LAMBDA_MAGNUM:
        return uuid.UUID(
            request.scope["aws.event"]["requestContext"]["authorizer"]["jwt"]["claims"][
                "sub"
            ]
        )

    if user_id := settings.test_user_id:
        return user_id

    return uuid.uuid4()


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


@lru_cache
def create_parkinglot_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ParkinglotRepository:
    if settings.dynamo_table:
        return DynamodbParkinglotRepository(settings.dynamo_table)
    return RamParkinglotRepository()


@lru_cache
def create_parkinglot_search_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ParkinglotSearchRepository:
    if settings.dynamo_table and settings.h3_cell_index:
        return DynamodbParkinglotSearchRepository(
            settings.dynamo_table,
            settings.h3_cell_index,
        )
    return RamParkinglotSearchRepository()
