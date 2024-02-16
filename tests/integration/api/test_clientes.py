from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from tests.fixtures.factories import NewTransactionRequestModelFactory
import pytest

pytestmark = pytest.mark.asyncio


class TestClientesAPI:
    """Test cases for /clientes/{id}"""

    @pytest.mark.skip
    async def test_return_all_transactions(self, client: AsyncClient, async_db: AsyncSession):
        response = await client.get('/clientes/1/extrato')
        assert response.status_code == status.HTTP_200_OK

    async def test_create_transaction_success(self, client: AsyncClient, async_db: AsyncSession):
        request = NewTransactionRequestModelFactory.build()

        response = await client.post('/clientes/1/transacoes', json=request.model_dump(by_alias=True),
                                    headers={"Content-type": "application/json"})

        assert response.status_code == status.HTTP_200_OK
