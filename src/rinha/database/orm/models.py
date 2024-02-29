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


class ClientModel(Base):
    __tablename__ = "clientes"

    limit: Mapped[int] = mapped_column("limite")
    balance: Mapped[int] = mapped_column("saldo", default=0)

    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel", lazy="joined", order_by="desc(TransactionModel.created_at)"
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


#     # banco exibindo hora errada.
# >>> import pytz
# >>> tz = pytz.timezone("America/Sao_Paulo")
# >>> datetime_str = '2024-02-29T01:22:37.411142-03:00'
# >>> datetime_format = '%Y-%m-%dT%H:%M:%S.%f%z'
# >>> parsed_datetime = datetime.strptime(datetime_str, datetime_format)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# NameError: name 'datetime' is not defined. Did you forget to import 'datetime'?
# >>> from datetime import datetime
# >>> parsed_datetime = datetime.strptime(datetime_str, datetime_format)
# >>> parsed_datetime
# datetime.datetime(2024, 2, 29, 1, 22, 37, 411142, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=75600)))
# >>> tz.localize(parsed_datetime
# ... )
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/home/murilo/workspace/rinha-backend-2024-q1-python/.venv/lib/python3.12/site-packages/pytz/tzinfo.py", line 321, in localize
#     raise ValueError('Not naive datetime (tzinfo is already set)')
# ValueError: Not naive datetime (tzinfo is already set)
# >>> gmt = pytz.timezone("UTC")
# >>> parsed_datetime.astimezone(gmt)
# datetime.datetime(2024, 2, 29, 4, 22, 37, 411142, tzinfo=<UTC>)
# >>> parsed_datetime.strftime(datetime_format)
# '2024-02-29T01:22:37.411142-0300'
# >>> t = parsed_datetime.astimezone(gmt)
# >>> t.strftime(datetime_format)
# '2024-02-29T04:22:37.411142+0000'
# >>>
