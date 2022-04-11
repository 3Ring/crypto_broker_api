from project.app import db
from project.models import Clients, Keys, Transactions, Users


def send_key(autocommit=True) -> Keys:
    _key = Keys()
    db.session.add(_key)
    if autocommit == True:
        db.session.commit()
    key = {
        "id": _key.id,
        "key": _key.key,
    }
    return key


def send_client(name: str, key_id: int, autocommit=True) -> Clients:
    _client = Clients(name=name, key_id=key_id)
    db.session.add(_client)
    if autocommit == True:
        db.session.commit()
    client = {
        "id": _client.id,
        "name": _client.name,
        "key": _client.key,
        "key_id": _client.key_id,
    }
    return client


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
    usd_amount: int, user_id: int, client_id: int, autocommit=True
) -> Transactions:
    tran = Transactions.create(
        usd_amount=usd_amount, user_id=user_id, client_id=client_id
    )
    if autocommit == True:
        db.session.commit()
    return tran


def fill_mock() -> dict[Keys, Clients, Users, Transactions]:
    key = send_key()
    client = send_client("chase", key["id"])
    user = send_user(client_id=client["id"])

    return {
        "key": key,
        "client": client,
        "user": user,
    }
