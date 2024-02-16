from datetime import datetime
from typing import Tuple

from pydantic import BaseModel, Field

from src.rinha.domain.enums.operation_type import OperationTypes


class BalanceDTO(BaseModel):
    total: int
    date: datetime = Field(alias="data_extrato")
    limit: int = Field(alias="limit")


class TransactionsDTO(BaseModel):
    value: int = Field(alias="valor")
    description: str = Field(alias="descricao")
    type: OperationTypes = Field(alias="tipo")
    created_at: datetime = Field(alias="realizada_em")


class QueryTransactionsResponse(BaseModel):
    balance: BalanceDTO = Field(alias="saldo")
    recent_transactions: Tuple[TransactionsDTO] = Field(alias="ultimas_transacoes")
