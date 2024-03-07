import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from src.rinha.config.settings import TIMEZONE, UTC_TIMEZONE
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

    @field_validator("created_at")
    @classmethod
    def naive_to_aware(cls, v: datetime.datetime) -> datetime.datetime:
        if not v.tzinfo:
            utc = UTC_TIMEZONE.localize(v)
            return utc.astimezone(TIMEZONE)
        return v.astimezone(TIMEZONE)


class ClientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    limit: int
    balance: int

    def update_balance(self, value: int, operation_type: OperationTypes) -> None:
        operation_value = (
            value if operation_type == OperationTypes.CREDIT else value * -1
        )
        new_balance = self.balance + operation_value
        if new_balance < (self.limit * -1):
            raise ValueError("Valor informado está acima do limite.")
        self.balance = new_balance


class ClientSchemaWithTransactions(ClientSchema):
    transactions: list[TransactionSchema] = []
