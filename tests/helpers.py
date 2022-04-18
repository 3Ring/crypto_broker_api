from project.app import db
from project.models import Clients, Keys, Transactions, Users


def send_key(autocommit=True) -> Keys:
    """
    It creates a mock key, adds it to the database, and returns the key

    :param autocommit: If True, the database will be committed after the key is added, defaults to True
    to the database when you call db.session.commit(), defaults to True (optional)
    :return: A dictionary with the id and key of the newly created key.
    """
    _key = Keys()
    db.session.add(_key)
    if autocommit == True:
        db.session.commit()
    return {
        "id": _key.id if autocommit == True else None,
        "key": _key.key,
    }


def send_client(name: str, key_id: int, autocommit=True) -> Clients:
    """
    Creates a mock client, adds it to the database, and returns the client

    :param name: The name of the client
    :param key_id: client's key id
    :param autocommit: If True, the database will be committed after the client is added, defaults to True
    :return: A dictionary with the client's id, name, key, and key_id.
    """
    _client = Clients(name=name, key_id=key_id)
    db.session.add(_client)
    if autocommit == True:
        db.session.commit()
    return {
        "id": _client.id if autocommit == True else None,
        "name": _client.name,
        "key": _client.key,
        "key_id": _client.key_id,
    }


def send_user(
    client_id: int,
    BTC: float = 0.0,
    ETH: float = 0.0,
    DOGE: float = 0.0,
    USDT: float = 0.0,
    BNB: float = 0.0,
    BTC_auth: bool = True,
    ETH_auth: bool = True,
    DOGE_auth: bool = True,
    USDT_auth: bool = True,
    BNB_auth: bool = True,
    autocommit: bool = True,
) -> Users:
    """
    Creates a mock user, adds it to the database, and returns the user

    :param client_id: id of the client hosting the user,
    :param BTC: user's BTC holdings,
    :param ETH: user's ETH holdings,
    :param DOGE: user's DOGE holdings
    :param USDT: user's USDT holdings,
    :param BNB: user's BNB holdings,
    :param BTC_auth: boolean representing if the user is authorized to trade BTC, defaults to True
    :param ETH_auth: boolean representing if the user is authorized to trade ETH, defaults to True
    :param DOGE_auth: boolean representing if the user is authorized to trade DOGE, defaults to True
    :param USDT_auth: boolean representing if the user is authorized to trade USDT, defaults to True
    :param BNB_auth: boolean representing if the user is authorized to trade BNB, defaults to True
    :param autocommit: If True, the database will be committed after the user is added, defaults to True
    :return: A dictionary
    """
    _user = Users(
        client_id=client_id,
        BTC=BTC,
        ETH=ETH,
        DOGE=DOGE,
        USDT=USDT,
        BNB=BNB,
        BTC_auth=BTC_auth,
        ETH_auth=ETH_auth,
        DOGE_auth=DOGE_auth,
        USDT_auth=USDT_auth,
        BNB_auth=BNB_auth,
    )
    db.session.add(_user)
    if autocommit == True:
        db.session.commit()
    user = {
        "id": _user.id,
        "client_id": _user.client_id,
        "BTC": _user.BTC,
        "ETH": _user.ETH,
        "DOGE": _user.DOGE,
        "USDT": _user.USDT,
        "BNB": _user.BNB,
    }
    return user


def send_transaction(
    usd_amount: float,
    user_id: int,
    client_id: int,
    inc_key: str = None,
    autocommit=True,
) -> Transactions:
    """
    It creates a mock transaction, adds it to the database and returns the transaction

    :param usd_amount: transaction amount in USD (positive for incoming buys, negative for incoming sells),
    :param user_id: id of user for whom the transaction was initiated,
    :param client_id: id of the client initiating the transaction,
    :param inc_key: client confirmation key (used in sell orders),
    :param autocommit: If True, the database will be committed after the transaction is added, defaults to True
    :return: A new transaction object
    """
    tran = Transactions.create(
        usd_amount=usd_amount, user_id=user_id, client_id=client_id, inc_key=inc_key
    )
    if autocommit == True:
        db.session.commit()
    return tran


def fill_mock() -> dict[Keys, Clients, Users, Transactions]:
    """
    shortcut function to create a baseline for testing.
    Creates a key, client, and user
    """
    key = send_key()
    client = send_client("chase", key["id"])
    user = send_user(client_id=client["id"])

    return {
        "key": key,
        "client": client,
        "user": user,
    }
