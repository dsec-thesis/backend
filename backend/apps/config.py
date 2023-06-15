from typing import Literal
from uuid import UUID

from pydantic import BaseSettings

Env = Literal["local", "aws_lambda_mangum"]


class Settings(BaseSettings):
    dynamo_table: str = ""
    h3_cell_index: str = ""
    sns_topic_arn: str = ""
    env: Env = "local"
    test_user_id: UUID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

    class Config:
        frozen = True
