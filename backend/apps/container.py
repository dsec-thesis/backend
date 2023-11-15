from dependency_injector import containers, providers

from backend.apps.config import Settings
from backend.contexts.booking.infrastructure import (
    DynamodbBookingRepository,
    RamBookingRepository,
)
from backend.contexts.parkinglot.infrastructure import (
    DynamodbParkinglotRepository,
    RamParkinglotRepository,
)
from backend.contexts.searcher.infraestructure import (
    DynamodbParkinglotSearchRepository,
    RamParkinglotSearchRepository,
)
from backend.contexts.shared.infrastructure import RamEventBus, SnsEventBus


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[".api", ".events"])

    config = providers.Configuration(pydantic_settings=[Settings()])

    local_booking_repository = providers.Singleton(
        RamBookingRepository,
    )
    dynamo_booking_repository = providers.Singleton(
        DynamodbBookingRepository,
        table_name=config.dynamo_table,
        inverted_index=config.inverted_index,
    )
    booking_repository = providers.Selector(
        config.env,
        local=local_booking_repository,
        aws_lambda_mangum=dynamo_booking_repository,
    )

    local_parkinglot_repository = providers.Singleton(
        RamParkinglotRepository,
    )
    dynamo_parkinglot_repository = providers.Singleton(
        DynamodbParkinglotRepository,
        table_name=config.dynamo_table,
        inverted_index=config.inverted_index,
    )
    parkinglot_repository = providers.Selector(
        config.env,
        local=local_parkinglot_repository,
        aws_lambda_mangum=dynamo_parkinglot_repository,
    )

    local_parkinglot_search_repository = providers.Singleton(
        RamParkinglotSearchRepository,
    )
    dynamo_parkinglot_search_repository = providers.Singleton(
        DynamodbParkinglotSearchRepository,
        table_name=config.dynamo_table,
        index_name=config.h3_cell_index,
    )
    parkinglot_search_repository = providers.Selector(
        config.env,
        local=local_parkinglot_search_repository,
        aws_lambda_mangum=dynamo_parkinglot_search_repository,
    )

    local_eventbus = providers.Singleton(RamEventBus)
    sns_eventbus = providers.Singleton(
        SnsEventBus,
        topic_arn=config.sns_topic_arn,
    )
    eventbus = providers.Selector(
        config.env,
        local=local_eventbus,
        aws_lambda_mangum=sns_eventbus,
    )
