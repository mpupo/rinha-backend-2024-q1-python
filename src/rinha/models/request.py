from pydantic import BaseModel, Field

from src.rinha.domain.enums.operation_type import OperationTypes


class NewTransactionRequest(BaseModel):
    value = Field(int, alias="valor")
    description = Field(str, alias="descricao")
    type = Field(OperationTypes, alias="tipo")
