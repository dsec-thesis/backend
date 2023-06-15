import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request

from backend.apps.config import Env
from backend.apps.container import Container


@inject
def get_user_id(
    request: Request,
    env: Env = Depends(Provide[Container.config.env]),
    test_user_id: uuid.UUID = Depends(Provide[Container.config.test_user_id]),
) -> uuid.UUID:
    if env == "local":
        return test_user_id
    return uuid.UUID(
        request.scope["aws.event"]["requestContext"]["authorizer"]["jwt"]["claims"][
            "sub"
        ]
    )
