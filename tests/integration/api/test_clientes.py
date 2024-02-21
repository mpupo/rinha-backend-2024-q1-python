from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from src.rinha.database.orm.models import TransactionModel, ClientModel#, client_transaction_association
from tests.fixtures.factories import NewTransactionRequestModelFactory
import sqlalchemy as sa
import pytest

pytestmark = pytest.mark.asyncio


class TestClientesAPI:
    """Test cases for /clientes/{id}"""

    @pytest.mark.skip
    async def test_return_all_transactions(self, client: AsyncClient, async_db: AsyncSession):
        response = await client.get('/clientes/1/extrato')
        assert response.status_code == status.HTTP_200_OK

    async def test_create_transaction_success(self, client: AsyncClient, async_db: AsyncSession):
        request = NewTransactionRequestModelFactory.build(tipo="c", valor=1000)

        response = await client.post('/clientes/1/transacoes', json=request.model_dump(by_alias=True),
                                    headers={"Content-type": "application/json"})
        
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert set(['limite', 'saldo']).issubset(data)
        assert data['limite'] == 1000 * 100
        assert data['saldo'] == request.value

        latest_transaction = (await async_db.execute(
            sa.select(TransactionModel).filter(TransactionModel.cliente_id == 1).order_by(sa.desc(TransactionModel.id)).limit(1)
        )).scalar_one_or_none()

        assert latest_transaction.valor == request.value
        assert latest_transaction.tipo == request.type
        assert latest_transaction.descricao == request.description

        await async_db.commit()

        updated_client = (await async_db.execute(
            sa.select(ClientModel).filter(ClientModel.id == 1).order_by(sa.desc(ClientModel.id)).limit(1)
        )).scalar_one_or_none()

        assert updated_client.saldo == request.value

        await async_db.commit()



        #count_association = (await async_db.execute(sa.select(sa.func.count()).select_from(client_transaction_association))).scalar()
        #assert count_association > 0
