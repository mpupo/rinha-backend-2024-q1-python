from pydantic import BaseModel, Field

from src.rinha.domain.enums.operation_type import OperationTypes


class NewTransactionRequest(BaseModel):
    value: int = Field( alias="valor")
    description: str = Field(alias="descricao")
    type: OperationTypes = Field(alias="tipo")
