from pymongo import MongoClient

from config.config import Config


class MongoConnection:
    _connection_name = ''
    _collection_name = ''
    _db_name = ''

    def __init__(self):
        config = Config()
        username = config.get(self._connection_name, 'username')
        password = config.get(self._connection_name, 'password')
        host = config.get(self._connection_name, 'host')
        port = config.get(self._connection_name, 'port')
        self.connection = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/', maxPoolSize=50)
        self.collection = self.connection[self._db_name][self._collection_name]

    def update(self, query, data):
        modification = {'$set': data}
        return self.collection.update_many(query, modification)

    def exist(self, query):
        peer = self.collection.count(query)
        return peer > 0

    def delete(self, query):
        return self.collection.delete_many(query)

    def find_one(self, query):
        return self.collection.find_one(query)

    def insert_many(self, data):
        return self.collection.insert_many(data)

    def insert_one(self, data):
        return self.collection.insert_one(data)

    def insert_one_ignore_duplicate(self, data):
        try:
            return self.collection.insert_one(data)
        except:
            pass

    def update_one_upsert(self, query, new_date):
        return self.collection.update_one(query, {
            '$set': new_date
        }, upsert=True)

    def insert_many_ignore_duplicate(self, docs):
        try:
            return self.collection.insert_many(docs, ordered=False)
        except:
            pass

    def bulk_execute(self, bulk):
        return self.collection.bulk_write(bulk)
