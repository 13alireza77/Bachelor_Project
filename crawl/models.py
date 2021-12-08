from components.mongo import MongoConnection


class PostDb(MongoConnection):
    _db_name = 'divar'
    _collection_name = 'posts'
    _connection_name = 'mongo'
