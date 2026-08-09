import pymongo
from server.config import settings
from pymongo.errors import ConnectionFailure

_client = None


def get_database():
    global _client
    if _client is None:
        try:
            _client = pymongo.MongoClient(settings.MONGODB_URI)
            _client.admin.command("ping")
        except ConnectionFailure:
            return None
    return _client[settings.MONGODB_DB_NAME]


def get_db():
    return get_database()
