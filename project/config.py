

class BaseConfig():
    db_password = "SuperSecretCode"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = db_password
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{db_password}@crypto_host:5432/crypto_db"

class DevConfig(BaseConfig):
    pass

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
