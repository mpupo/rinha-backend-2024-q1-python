from datetime import datetime
from typing import Tuple

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from src.rinha.config.settings import TIMEZONE
from src.rinha.domain.enums.operation_type import OperationTypes


class BalanceDTO(BaseModel):
    total: int
    date: AwareDatetime = Field(
        serialization_alias="data_extrato",
        default_factory=lambda: datetime.now(TIMEZONE),
    )
    limit: int = Field(serialization_alias="limite")


class TransactionsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    value: int = Field(serialization_alias="valor")
    description: str = Field(serialization_alias="descricao")
    type: OperationTypes = Field(serialization_alias="tipo")
    created_at: AwareDatetime = Field(serialization_alias="realizada_em")


class QueryTransactionsResponse(BaseModel):
    balance: BalanceDTO = Field(serialization_alias="saldo")
    recent_transactions: Tuple[TransactionsDTO, ...] = Field(
        serialization_alias="ultimas_transacoes"
    )


class NewTransactionResponse(BaseModel):
    limit: int = Field(serialization_alias="limite")
    balance: int = Field(serialization_alias="saldo")
