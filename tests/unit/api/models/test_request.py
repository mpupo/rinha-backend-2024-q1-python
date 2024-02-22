import pytest
from pydantic import ValidationError

from src.rinha.api.models import NewTransactionRequest


@pytest.fixture
def new_transaction_request() -> dict:
    return {"valor": 1000, "tipo": "c", "descricao": "descricao"}


class TestNewTransactionRequest:
    def test_should_parse_a_request(self, new_transaction_request):
        result = NewTransactionRequest(**new_transaction_request)

        assert result.value == new_transaction_request["valor"]
        assert result.description == new_transaction_request["descricao"]
        assert result.type == new_transaction_request["tipo"]

    def test_should_reject_a_request_with_wrong_type(self, new_transaction_request):
        with pytest.raises(ValidationError):
            wrong_value = new_transaction_request.copy()
            wrong_value["tipo"] = "A"
            NewTransactionRequest(**wrong_value)
