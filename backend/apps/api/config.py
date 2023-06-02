from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseSettings


class Env(Enum):
    LOCAL = "LOCAL"
    AWS_LAMBDA_MAGNUM = "AWS_LAMBDA_MANGUM"


class Settings(BaseSettings):
    dynamo_table: Optional[str] = None
    h3_cell_index: Optional[str] = None
    sns_topic_arn: Optional[str] = None
    env: Env = Env.LOCAL
    test_user_id: Optional[UUID] = None

    class Config:
        frozen = True
