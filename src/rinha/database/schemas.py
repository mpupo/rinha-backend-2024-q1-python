import datetime
from pydantic import BaseModel

from src.rinha.domain.enums.operation_type import OperationTypes
from src.rinha.domain.models.transaction import Transaction


class TransactionBaseSchema(BaseModel):
    cliente_id: int
    tipo: OperationTypes
    descricao: str

    @classmethod
    def from_domain(cls, transaction: Transaction):
        return cls(
            id=transaction.id,
            cliente_id=transaction.client_id,
            tipo=transaction.type,
            descricao=transaction.description,
            realizada_em=transaction.created_at,
        )

    def to_domain(self):
        return Transaction(
            id=self.id,
            client_id=self.cliente_id,
            type=self.tipo,
            description=self.descricao,
            created_at=self.realizada_em,
        )


class TransactionCreateSchema(TransactionBaseSchema):
    pass


class TransactionSchema(TransactionBaseSchema):
    id: int
    realizada_em: datetime.datetime

    class Config:
        orm_mode = True
