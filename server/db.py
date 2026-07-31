import pymongo
from pymongo.errors import ConnectionFailure


def init_connection(uri: str):
    try:
        client = pymongo.MongoClient(uri)
        client.admin.command("ping")
        return client
    except ConnectionFailure:
        return None


def get_db(client, db_name: str):
    if client:
        return client[db_name]
    return None
