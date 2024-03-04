import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.rinha.config.settings import settings
from src.rinha.database.orm.models import (
    ClientModel,
    TransactionModel,
)
from tests.fixtures.factories import NewTransactionRequestModelFactory
from tests.utils.asserts import assert_date_includes_timezone

pytestmark = pytest.mark.asyncio


class TestClientesAPI:
    """Test cases for /clientes/{id}"""

    async def test_create_transaction_success(
        self, client: AsyncClient, async_db: AsyncSession
    ):
        request = NewTransactionRequestModelFactory.build(tipo="c", valor=1000)

        response = await client.post(
            "/clientes/1/transacoes",
            json=request.model_dump(by_alias=True),
            headers={"Content-type": "application/json"},
        )

        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert set(["limite", "saldo"]).issubset(data)
        assert data["limite"] == 1000 * 100
        assert data["saldo"] == request.value

        latest_transaction = (
            await async_db.execute(
                sa.select(TransactionModel)
                .filter(TransactionModel.client_id == 1)
                .order_by(sa.desc(TransactionModel.id))
                .fetch(1)
            )
        ).scalar_one_or_none()

        assert latest_transaction is not None
        assert latest_transaction.value == request.value
        assert latest_transaction.type == request.type
        assert latest_transaction.description == request.description

        updated_client = (
            (
                await async_db.execute(
                    sa.select(ClientModel)
                    .filter(ClientModel.id == 1)
                    .order_by(sa.desc(ClientModel.id))
                    .fetch(1)
                )
            )
            .unique()
            .scalar_one_or_none()
        )

        assert updated_client is not None
        assert updated_client.balance == request.value

    async def test_create_transaction_success_balance_not_changed(
        self, client: AsyncClient, async_db: AsyncSession
    ):
        first = NewTransactionRequestModelFactory.build(tipo="d", valor=100000)
        second = NewTransactionRequestModelFactory.build(tipo="d", valor=1)

        response_first = await client.post(
            "/clientes/1/transacoes",
            json=first.model_dump(by_alias=True),
            headers={"Content-type": "application/json"},
        )
        _ = await client.post(
            "/clientes/1/transacoes",
            json=second.model_dump(by_alias=True),
            headers={"Content-type": "application/json"},
        )

        data_first = response_first.json()
        assert response_first.status_code == status.HTTP_200_OK
        assert set(["limite", "saldo"]).issubset(data_first)
        assert data_first["limite"] == 1000 * 100
        assert data_first["saldo"] == first.value * -1

        latest_transaction = (
            await async_db.execute(
                sa.select(TransactionModel)
                .filter(TransactionModel.client_id == 1)
                .order_by(sa.desc(TransactionModel.id))
                .fetch(1)
            )
        ).scalar_one_or_none()

        assert latest_transaction is not None
        assert latest_transaction.value == first.value
        assert latest_transaction.type == first.type
        assert latest_transaction.description == first.description

        updated_client = (
            (
                await async_db.execute(
                    sa.select(ClientModel)
                    .filter(ClientModel.id == 1)
                    .order_by(sa.desc(ClientModel.id))
                    .fetch(1)
                )
            )
            .unique()
            .scalar_one_or_none()
        )

        assert updated_client is not None
        assert updated_client.balance < (second.value + first.value)

    async def test_list_transaction_success(
        self, client: AsyncClient, async_db: AsyncSession
    ):
        requests = NewTransactionRequestModelFactory.batch(
            size=11, tipo="c", valor=1000
        )

        for request in requests:
            await client.post(
                "/clientes/1/transacoes",
                json=request.model_dump(by_alias=True),
                headers={"Content-type": "application/json"},
            )

        response = await client.get(
            "/clientes/1/extrato",
            headers={"Content-type": "application/json"},
        )

        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert set(["saldo", "ultimas_transacoes"]).issubset(data)
        assert data["saldo"]["total"] == 1000 * 11
        assert data["saldo"]["limite"] == 1000 * 100
        assert_date_includes_timezone(data["saldo"]["data_extrato"], settings.TIMEZONE)

        assert len(data["ultimas_transacoes"]) == 10
        all(
            assert_date_includes_timezone(transacao["realizada_em"], settings.TIMEZONE)
            for transacao in data["ultimas_transacoes"]
        )
