from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from tests.fixtures.factories import NewTransactionRequestModelFactory
import pytest

pytestmark = pytest.mark.asyncio


class TestClientesAPI:
    """Test cases for /clientes/{id}"""

    async def test_return_all_transactions(self, client: TestClient):
        pass

    async def test_create_transaction_success(self, client: TestClient):
        request = NewTransactionRequestModelFactory.build()

        response = client.post('/clientes/1/transacoes', json=request.model_dump(by_alias=True),
                                    headers={"Content-type": "application/json"})

        assert response.status_code == status.HTTP_200_OK
