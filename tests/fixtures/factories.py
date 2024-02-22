from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use
from src.rinha.api.models import NewTransactionRequest
from src.rinha.domain.enums import OperationTypes


class NewTransactionRequestModelFactory(ModelFactory[NewTransactionRequest]):
    type = Use(
        ModelFactory.__random__.choice, [member.value for member in OperationTypes]
    )
