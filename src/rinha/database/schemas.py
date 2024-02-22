import datetime
from pydantic import BaseModel, ConfigDict

from src.rinha.domain.enums.operation_type import OperationTypes


class TransactionBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: int
    type: OperationTypes
    description: str
    value: int


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionSchema(TransactionBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime


class ClientBaseSchema(BaseModel):
    limit: int


class ClienteUpdateSchema(BaseModel):
    balance: int


class ClientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
