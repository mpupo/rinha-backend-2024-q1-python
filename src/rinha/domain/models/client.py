from pydantic import BaseModel

from src.rinha.domain.enums.operation_type import OperationTypes
from src.rinha.domain.models.transaction import Transaction


class Client(BaseModel):
    id: int | None = None
    limit: int
    balance: int = 0
    transactions: list[Transaction] = []

    @staticmethod
    def update_balance(current_balance, limit,  new_balance: int, operation_type: OperationTypes) -> int:
        value = new_balance if operation_type == OperationTypes.CREDIT else new_balance * -1
        final_balance = current_balance + value
        if final_balance > limit:
            raise ValueError("Valor informado está acima do limite.")
        return final_balance

"""     def update_balance(self, new_balance: int, operation_type: OperationTypes) -> None:
        value = new_balance if operation_type == OperationTypes.CREDIT else new_balance * -1
        final_balance = self.balance + value
        if final_balance > self.limit:
            raise ValueError("Valor informado está acima do limite.")
        self.balance = final_balance """