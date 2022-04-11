import secrets
from datetime import datetime

from project.app import db
from project.globals import ACCEPTED_SYMBOLS


class Users(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    BTC = db.Column(db.Float, default=0.0)
    BTC_auth = db.Column(db.Boolean, default=False)
    ETH = db.Column(db.Float, default=0.0)
    ETH_auth = db.Column(db.Boolean, default=False)
    DOGE = db.Column(db.Float, default=0.0)
    DOGE_auth = db.Column(db.Boolean, default=False)
    USDT = db.Column(db.Float, default=0.0)
    USDT_auth = db.Column(db.Boolean, default=False)
    BNB = db.Column(db.Float, default=0.0)
    BNB_auth = db.Column(db.Boolean, default=False)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    def purchase(self, symbol: str, usd_amount: float):
        from project.helpers import convert_to_crypto
        """This is in place of a purchasing API"""
        self._allowed_currency(symbol)
        current = getattr(self, symbol)
        new = convert_to_crypto(usd_amount, symbol)
        setattr(self, symbol, current + new)

    def _allowed_currency(self, symbol: str):
        """Checks that the user is allowed to trade in the currency"""
        from project.exceptions import InvalidSymbolError, UnauthorizedCurrencyError
        try:
            assert symbol in ACCEPTED_SYMBOLS
        except AssertionError:
            raise InvalidSymbolError
        if getattr(self, f"{symbol}_auth") is False:
            raise UnauthorizedCurrencyError(self, symbol)

    def auth_to_dict(self) -> dict:
        """Returns a dict containing the User's details and the currencies which they are authorized to trade in"""
        data = {
            "id": self.id,
            "provider": Clients.query.get(self.client_id).name,
            "auths": [],
        }
        for symbol in ACCEPTED_SYMBOLS:
            if getattr(self, f"{symbol}_auth") is True:
                data["auths"].append(symbol)
        return data

    def balance_to_dict(self) -> dict:
        """Returns a dict containing the User's details and their holdings"""
        data = {
            "id": self.id,
            "provider": Clients.query.get(self.client_id).name,
            "balances": {},
        }
        for symbol in ACCEPTED_SYMBOLS:
            if getattr(self, symbol) != 0.0:
                data["balances"][symbol] = getattr(self, symbol)
        return data


class Clients(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    key_id = db.Column(db.Integer, db.ForeignKey("keys.id"), nullable=False)

    @property
    def key(self):
        return Keys.query.get(self.key_id).key

    def auth_key(self, key: str):
        """Checks that API key is valid"""
        from project.exceptions import InvalidTokenError

        if not secrets.compare_digest(key, Keys.query.get(self.key_id).key):
            raise InvalidTokenError


class Keys(db.Model):
    __tablename__ = "keys"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False, default=secrets.token_urlsafe())


class Transactions(db.Model):
    """This table represents incoming varified payments. used to confirm and release assets through API"""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Integer)
    inc_time = db.Column(db.DateTime, default=datetime.utcnow())
    complete_time = db.Column(db.DateTime)
    complete = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    @classmethod
    def create(cls, usd_amount: int, user_id: int, client_id: int):
        """creates and adds new transaction to the database"""
        new = cls(usd_amount=usd_amount, user_id=user_id, client_id=client_id)
        db.session.add(new)
        return new

    def completed(self):
        """Sets the transactions to 'complete' this is to ensure the same transaction is not executed twice"""
        self.complete = True
        self.complete_time = datetime.utcnow()
