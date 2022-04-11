from flask import Blueprint, jsonify, request

from project.exceptions import (
    DuplicatePaymentError,
    InsufficientCurrencyError,
    InvalidSymbolError,
    InvalidTokenError,
    TransactionMismatchError,
    TransactionNotFoundError,
    UnauthorizedCurrencyError,
)
from project.helpers import (
    convert_to_usd,
    db_session,
    transaction,
    verify_currency,
    bad_request,
    error_response,
)
from project.models import Users, Clients, Transactions

api = Blueprint("main", __name__)


@api.before_request
def check_api_key():
    """pre-route request validation"""
    try:
        client_id = request.headers.get("client_id", type=int)
        if client_id is None:
            raise ValueError
    except (ValueError, TypeError):
        return bad_request("'client_id' header required")
    try:
        auth = request.headers.get("authorization", type=str)
        if auth is None:
            raise ValueError
    except ValueError:
        return bad_request("'Authorization' header required")
    client = Clients.query.get_or_404(client_id)
    try:
        client.auth_key(auth)
    except InvalidTokenError:
        return error_response(401, "invalid API key")


@api.route("/list/<int:id>", methods=["GET"])
def currency_list(id):
    """Currency list: For a given user, get the curriencies they can transact"""

    return jsonify(Users.query.get_or_404(id).auth_to_dict()), 200


@api.route("/buy/<int:id>/<symbol>/<int:usd_amount>", methods=["POST"])
def buy(id: int, symbol: str, usd_amount: int):
    """Buy: For a given User, buy a selected Currency"""

    with db_session():
        try:
            transaction_id = request.headers.get("transaction_id")
            if transaction_id is None:
                raise ValueError
        except ValueError:
            return bad_request("'transaction_id' header required")
        try:
            user = Users.query.with_for_update().get_or_404(id)
            with transaction(transaction_id, usd_amount, user.id):
                user.purchase(symbol, usd_amount)
        except InvalidSymbolError:
            return error_response(404, f"'{symbol}' is not a valid symbol")
        except TransactionNotFoundError:
            return error_response(401, "Transaction not found")
        except TransactionMismatchError:
            return error_response(401, "Transaction details do not match")
        except DuplicatePaymentError as e:
            return error_response(401, f"{e}")
        except UnauthorizedCurrencyError as e:
            return error_response(401, f"{e}")
    return "", 204


@api.route("/sell/<int:id>/<symbol>/<float:currency_amount>", methods=["POST"])
def sell(id: int, symbol: str, currency_amount: float):
    """Sell: for a given User, sell a selected Currency"""
    with db_session():
        user = Users.query.with_for_update().get(id)
        try:
            verify_currency(user, symbol, currency_amount)
            usd = convert_to_usd(currency_amount, symbol)
            setattr(user, symbol, getattr(user, symbol) - currency_amount)

            Transactions.create(
                usd_amount=-usd,
                user_id=user.id,
                client_id=int(request.headers.get("client_id")),
            )
        except InvalidSymbolError:
            return error_response(404, f"'{symbol}' is not a valid symbol")
        except InsufficientCurrencyError as e:
            return error_response(401, f"{e}")
    return "", 204


@api.route("/balances/<int:id>", methods=["GET"])
def balances(id):
    """Balances: For a given User, get a list of Balances"""
    return jsonify(Users.query.get_or_404(id).balance_to_dict()), 200