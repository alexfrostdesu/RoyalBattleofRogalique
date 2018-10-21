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

    def delete_all_saves(self):
        """
        Deletes all the entries in redis
        Requires python process stop, otherwise will be overritten by new entries
        """
        keys = self.connection.keys('*')
        for key in keys:
            self.delete(key)

    def short_info(self):
        """
        Prints all saved character classes, their lvl and user_id
        """
        keys = self.connection.keys('*')
        res = ""
        for key in keys:
            game = self.get_game(key)
            player = game.get_playerchar()
            lvl = player.get_lvl()
            cla = player.get_class()
            res += f"player {int(key)} of class {cla}:lvl {lvl}\n"
        print(res)

    def full_info(self):
        """
        Prints all the saved character's stats
        """
        keys = self.connection.keys('*')
        res = ""
        from events import StatusMessage
        for key in keys:
            game = self.get_game(key)
            player = game.get_playerchar()
            res += StatusMessage(player).stats_message() + '\n'
        print(res)
