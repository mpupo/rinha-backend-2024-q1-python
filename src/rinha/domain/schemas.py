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


class ClientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    limit: int
    balance: int

    def update_balance(self, new_balance: int, operation_type: OperationTypes) -> None:
        value = (
            new_balance if operation_type == OperationTypes.CREDIT else new_balance * -1
        )
        final_balance = self.balance + value
        if final_balance < (self.limit * -1):
            raise ValueError("Valor informado está acima do limite.")
        self.balance = final_balance
