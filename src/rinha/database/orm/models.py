# Create engine
import datetime
from sqlalchemy import create_engine
from sqlalchemy import String, ForeignKey, TIMESTAMP, func, Enum, Table, Column, Integer
from sqlalchemy.orm import (
    relationship,
    DeclarativeBase,
    Mapped,
    mapped_column,
)

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

    limite: Mapped[int]
    saldo: Mapped[int] = 0

    transacoes: Mapped[list["TransactionModel"]] = relationship("TransactionModel", lazy="selectin", back_populates="client")


class TransactionModel(Base):
    __tablename__ = "transacoes"

    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    tipo: Mapped[OperationTypes]
    valor: Mapped[int]
    descricao: Mapped[str] = mapped_column(String(40))
    realizada_em: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    client: Mapped["ClientModel"] = relationship("ClientModel", lazy="selectin", back_populates="transacoes")

# DATABASE_URL = "postgresql://username:password@localhost/db_name"
# engine = create_engine(DATABASE_URL)

# # Create tables
# Base.metadata.create_all(bind=engine)

# Create session
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
