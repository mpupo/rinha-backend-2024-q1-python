import datetime

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.rinha.domain.enums.operation_type import OperationTypes


class Base(DeclarativeBase):
    type_annotation_map = {
        OperationTypes: Enum(
            OperationTypes.DEBIT, OperationTypes.CREDIT, name="tipo_transacao"
        ),
    }

    id: Mapped[int] = mapped_column(primary_key=True, index=True)


# client_transaction_association = Table(
#     "clientes_transacoes",
#     Base.metadata,
#     Column("cliente_id", Integer, ForeignKey("clientes.id")),
#     Column("transacao_id", Integer, ForeignKey("transacoes.id")),
# )


class ClientModel(Base):
    __tablename__ = "clientes"

    limit: Mapped[int] = mapped_column("limite")
    balance: Mapped[int] = mapped_column("saldo", default=0)

    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel", lazy="dynamic", order_by="desc(TransactionModel.created_at)"
    )


class TransactionModel(Base):
    __tablename__ = "transacoes"

    client_id: Mapped[int] = mapped_column("cliente_id", ForeignKey("clientes.id"))
    type: Mapped[OperationTypes] = mapped_column("tipo")
    value: Mapped[int] = mapped_column("valor")
    description: Mapped[str] = mapped_column("descricao", String(40))
    created_at: Mapped[datetime.datetime] = mapped_column(
        "realizada_em", TIMESTAMP(timezone=True), server_default=func.now()
    )
