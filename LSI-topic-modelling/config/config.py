import os
import secrets
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class FlaskConfig:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)

    POSTGRES_USER = os.environ.get('DB_USER')
    POSTGRES_PW = os.environ.get('DB_PASSWORD')
    POSTGRES_URL = os.environ.get('DB_URL')
    POSTGRES_DB = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}"


class ClientConfig:
    DATA_DIRECTORY = "test_data"
    SANITIZED_FILES_DIRECTORY = "training_data"


class AnalyzerConfig:
    ISOCODE_LANGUAGE_MAP = {
            "en": "english",
            "de": "german",
            "fr": "french",
            "fi": "finnish",
            "ar": "arabic",
            "da": "danish",
            "nl": "dutch",
            "hu": "hungarian",
            "it": "italian",
            "no": "norwegian",
            "pt": "portuguese",
            "ro": "romanian",
            "ru": "russian",
            "es": "spanish",
            "sv": "swedish"
        }
    CUSTOM_STOPWORDS = ["--retracted--", "xxx@email.zz"]
    NUM_TOPICS = 16
    DEFAULT_TOP_N = 10 # The app returns this many results, if not otherwise specified in the request
