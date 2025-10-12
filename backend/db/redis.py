import redis
from .connection import Connection


class Redis:
    def __init__(self, con: Connection, db=0):
        self.host = con.host
        self.port = con.port
        self.client = redis.StrictRedis(
            host=con.host, port=con.port, decode_responses=True, db=db
        )

    def __repr__(self):
        return f"Redis(host={self.host}, port={self.port})"

    def __del__(self):
        self.client.close()

    def set(self, key, value):
        self.client.set(key, value)

    def hset(self, name, key, value):
        self.client.hset(name, key, value)

    def hsetm(self, name, mapping):
        self.client.hset(name, mapping=mapping)

    def setex(self, key, value, ex):
        self.client.setex(key, ex, value)

    def get(self, key):
        return self.client.get(key)

    def hget(self, name, key):
        return self.client.hget(name, key)

    def delete(self, key):
        self.client.delete(key)
