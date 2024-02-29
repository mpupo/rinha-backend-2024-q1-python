from pydantic import BaseModel, Field, PositiveInt

from src.rinha.domain.enums.operation_type import OperationTypes


class NewTransactionRequest(BaseModel):
    value: PositiveInt = Field(alias="valor")
    description: str = Field(alias="descricao", min_length=1, max_length=10)
    type: OperationTypes = Field(alias="tipo")
