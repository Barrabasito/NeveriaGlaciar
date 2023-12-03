class BaseConfig:
    USER_DB = "postgres"
    PASS_DB = "19100209"
    URL_DB = "localhost"
    NAME_DB = "NeveriaGlaciar"
    FULL_URL_DB = f"postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}"
    SQLALCHEMY_DATABASE_URI = FULL_URL_DB
    SECRET_KEY = "llave_secreta"
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
