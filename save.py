import pickle, redis, os

REDIS_URL = os.environ["REDIS_URL"]

class RedisConnection(object):

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = redis.from_url(self.connection_string)

    def set_value(self, key, value):
        """Sets the value of key to value"""
        self.connection.set(key, value)

    def get_value(self, key):
        """Gets value of a key"""
        return self.connection.get(key)

    def delete(self, key):
        """Deletes value by key"""
        self.connection.delete(key)

    def save_game(self, key, game):
        """Serializes game to binary and saves"""
        game_serialized = pickle.dumps(game)
        self.set_value(key, game_serialized)

    def get_game(self, key):
        """Returns deserialized game object"""
        serizalized = self.get_value(key)
        return pickle.loads(serizalized)

    def get_all_games(self):
        """Returns dictionary with payer_id's as keys, and games as values"""
        result = {}
        keys = self.connection.keys('*')
        for key in keys:
            result[int(key)] = self.get_game(key)
        return result
