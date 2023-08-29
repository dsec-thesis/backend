from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request

from backend.apps.config import Env
from backend.apps.container import Container
from backend.contexts.shared.domain import DriverId, OwnerId


@inject
def get_user_id(
    request: Request,
    env: Env = Depends(Provide[Container.config.env]),
    test_user_id: str = Depends(Provide[Container.config.test_user_id]),
) -> str:
    if env == "local":
        return test_user_id
    return request.scope["aws.event"]["requestContext"]["authorizer"]["jwt"]["claims"][
        "sub"
    ]


def get_driver_id(user_id: str = Depends(get_user_id)) -> DriverId:
    return DriverId(user_id)


def get_owner_id(user_id: str = Depends(get_user_id)) -> OwnerId:
    return OwnerId(user_id)
