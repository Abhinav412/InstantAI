from pymongo import MongoClient

class MongoRepository:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert(self, collection: str, document: dict):
        return self.db[collection].insert_one(document)

    def find_one(self, collection: str, query: dict):
        return self.db[collection].find_one(query)

    def update(self, collection: str, query: dict, update: dict):
        return self.db[collection].update_one(query, {"$set": update})
