import math
from contextlib import contextmanager
from typing import Tuple

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from project.globals import ACCEPTED_SYMBOLS
from project.app import db


@contextmanager
def db_session(autocommit: bool = True):
    """context manager for managing a database session"""
    try:
        yield db.session
        if autocommit:
            db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.remove()


from project.exceptions import (
    TransactionMismatchError,
    TransactionNotFoundError,
    InvalidSymbolError,
    DuplicatePaymentError,
    InsufficientCurrencyError,
)
from project.models import Users, Transactions


@contextmanager
def transaction(transaction_id: int, usd_amount: float, user_id: int) -> Transactions:
    """Verifies and completes transaction"""
    transaction = Transactions.query.with_for_update().get(transaction_id)
    if transaction is None:
        raise TransactionNotFoundError
    if transaction.usd_amount != usd_amount or transaction.user_id != user_id:
        raise TransactionMismatchError
    if transaction.complete:
        raise DuplicatePaymentError(transaction)
    yield transaction
    transaction.completed()


def convert_to_crypto(usd: float, symbol: str) -> float:
    """converts usd amounts to crypto.

    in a real application this would be though an API

    :param amount: The USD amount the user is spending
    :param symbol: The acronym representing the crypto you want to purchase, e.g. "BTC"
    :return: The amount of crypto acquired.
    """
    conversion = {
        "BTC": 0.0000233678,
        "ETH": 0.00030321,
        "DOGE": 8.10,
        "USDT": 1,
        "BNB": 0.00234261,
    }
    return usd * conversion[symbol]
 


def convert_to_usd(amount: float, symbol: str) -> float:
    """converts crypto to usd

    in a real application this would be though an API

    :param amount: The quantity crypto you want to convert to USD
    :param symbol: The acronym representing the crypto you want to convert, e.g. "BTC"
    :return: The amount of USD to be paid to the user.
    """

    conversion = {
        "BTC": 0.0000233678,
        "ETH": 0.00030321,
        "DOGE": 8.10,
        "USDT": 1,
        "BNB": 0.00234261,
    }
    return amount / conversion[symbol]


def error_response(status_code: int, message=None) -> Tuple[str, str]:
    """parses error responses to send

    :param status_code: The HTTP status code to return
    :param message: The error message to return to the client
    :return: A tuple of two strings.
    """
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message) -> Tuple[str, str]:
    """shorthand function for `error_response(400, message)`"""
    return error_response(400, message)


def verify_currency(user: Users, symbol: str, amount: float) -> None:
    """
    verifies that the user has enough of the currency they're trying to sell
    
    :param user: Users - The user object that you want to verify the currency for
    :param symbol: The currency symbol, e.g. "BTC"
    :param amount: The amount of currency to be verified
    """
    if symbol not in ACCEPTED_SYMBOLS:
        raise InvalidSymbolError
    try:
        assert amount <= getattr(user, symbol)
    except AssertionError:
        raise InsufficientCurrencyError(user, symbol, amount)
