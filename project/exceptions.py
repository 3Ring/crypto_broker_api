class TransactionNotFoundError(Exception):
    pass


class TransactionMismatchError(Exception):
    pass


class InsufficientCurrencyError(Exception):

    from project.models import Users

    def __init__(self, user: Users, symbol: str, amount: float, *args: object) -> None:
        super().__init__(*args)
        self.user = user
        self.symbol = symbol
        self.amount = amount

    def __str__(self) -> str:
        return f"Insufficient {self.symbol}. user_id {self.user.id} only owns {getattr(self.user, self.symbol)})"


class DuplicatePaymentError(Exception):

    from project.models import Transactions

    def __init__(self, transaction: Transactions, *args: object) -> None:
        super().__init__(*args)
        self.transaction = transaction

    def __str__(self) -> str:
        return f"transaction {self.transaction.id} Already completed. \nTransaction initiated at datetime_utc: {self.transaction.inc_time}\n Transaction completed at datetime_utc: {self.transaction.complete_time}"


class InvalidTokenError(Exception):
    pass


class InvalidSymbolError(Exception):
    pass


class UnauthorizedCurrencyError(Exception):
    from project.models import Users

    def __init__(self, user: Users, symbol: str, *args: object) -> None:
        super().__init__(*args)
        self.user = user
        self.symbol = symbol

    def __str__(self) -> str:
        return f"User {self.user.id} is not authorized to purchase {self.symbol}"
