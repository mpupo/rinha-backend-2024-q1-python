import pytest

from src.rinha.domain.enums.operation_type import OperationTypes
from src.rinha.domain.schemas import ClientSchema


class TestClientSchema:
    def test_update_balance_success(self):
        sut = ClientSchema(id=1, limit=1000, balance=1000)

        sut.update_balance(1000, operation_type=OperationTypes.CREDIT)

        assert sut.balance == 2000

    def test_update_balance_raise_error(self):
        sut = ClientSchema(id=1, limit=1000, balance=1000)

        with pytest.raises(ValueError):
            sut.update_balance(10000, operation_type=OperationTypes.DEBIT)
