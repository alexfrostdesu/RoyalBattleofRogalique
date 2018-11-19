from classes import *
from events import DialogMessage, StatusMessage
from bot_handler import BotHandler, Message
import random
import os
import traceback, functools, json

TOKEN = os.environ["TOKEN"]


class OutMessage():
    """Message to be sent to player"""

    def __init__(self, text, chat_id, player_id, keyboard=None):
        self.text = text
        self.chat_id = chat_id
        self.player_id = player_id
        self.keyboard = keyboard


class Game:
    def __init__(self, chat_id, player_id):
        self._player_id = player_id
        self._chat_id = chat_id
        self._game_state = 'Game Start'
        self._message_send_list = []
        self._first_launch = True
        self._keyboard = json.dumps({'keyboard': [self.get_state_input()], 'one_time_keyboard': False, 'resize_keyboard': True})

    def check_state(self):
        """
        Return current game state
        """
        return self._game_state

    def set_state(self, state):
        """
        Setting game state to another value
        """
        self._game_state = state
        self._keyboard = json.dumps(
             {'keyboard': [self.get_state_input()], 'one_time_keyboard': False, 'resize_keyboard': True})

    @functools.lru_cache(8)
    def get_game_states(self):
        return {'Game Start':{"func": self.game_start,
                              "input": ['Mage', 'Warrior', 'Rogue']},
            'Base':          {"func": self.base,
                              "input": ['Shop', 'Stats', 'Inventory', 'Find Monsters']},
            'Battle':        {"func": self.battle,
                              "input": None},
            'Battle Won':    {"func": self.won_battle,
                              "input": None},
            'Battle Choice': {"func": self.battle_choice,
                              "input": ['Attack', 'Retreat']},
            'Item Choice':   {"func": self.item_choice,
                              "input": ['Equip', 'Discard']},
            'Shop':          {"func": self.shop,
                              "input": ['Restore HP', 'Small Potion', 'Medium Potion', 'Attack Boost', 'Magic Boost', 'Exit']}}

    def get_playerchar(self):
        """
        Get current game player character
        """
        return self.playerchar

    def enqueue_message(self, text, chat_id, player_id, keyboard=None):
        """
        Adds message to a send list
        """
        self._message_send_list.append(OutMessage(text, chat_id, player_id, keyboard))

    def send_all_messages(self):
        """
        Clears the message list, and returs all the messages in it
        """
        messages = self._message_send_list
        self._message_send_list = []
        return messages

    def get_state_function(self):
        """Returns a function appropriate for current state"""
        return self.get_game_states()[self._game_state]["func"]

    def get_state_input(self):
        """Returns input approptiate for current state"""
        return self.get_game_states()[self._game_state]["input"]

    def process_incoming_message(self, message):
        """
        Takes incoming message
        processes basen on a game state
        and returns reply messages
        """
        fnc = self.get_state_function()
        fnc(message)
        return self.send_all_messages()

#   Lazy copypaste 2 lines at a time #

    def send_stats(self, char):
        """
        Shows the stats message
        """
        _stats = StatusMessage(char).stats_message()
        self.enqueue_message(_stats, self._chat_id, self._player_id)

    def send_inventory(self, char):
        """
        Shows the inventory message
        """
        _inventory = StatusMessage(char).inventory_message()
        self.enqueue_message(_inventory, self._chat_id, self._player_id)

    def roll(self, number):
        roll = random.randint(1, 6)
        return roll >= number

#   Game start block #

    def game_start(self, message):
        """
        Character selection state
        Intended for single use
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message(
                'Please input correct class name', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(DialogMessage(
                'start_game').get_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            # creating player character
            self.playerchar = eval("{}()".format(message))
            self.send_stats(self.playerchar)
            self.set_state('Base')
            self.enqueue_message(DialogMessage(
                'base').get_message(), self._chat_id, self._player_id, self._keyboard)

    def base(self, message):
        """
        Base state
        Adventure starts from here
        Inventory, status, shop
        """
        # keyboard = json.dumps({'keyboard': [self.get_state_input()], 'one_time_keyboard': True, 'resize_keyboard': True})
        # keyboard = None
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(DialogMessage(
                'base').get_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            if message == 'Stats':
                self.send_stats(self.playerchar)
                self.enqueue_message(DialogMessage(
                    'base').get_message(), self._chat_id, self._player_id, self._keyboard)
            elif message == 'Inventory':
                self.send_inventory(self.playerchar)
                self.enqueue_message(DialogMessage(
                    'base').get_message(), self._chat_id, self._player_id, self._keyboard)
            elif message == 'Find Monsters':
                self.set_state('Battle Choice')
                self.create_battle()
            elif message == 'Shop':
                self.set_state('Shop')
                self.enqueue_message(StatusMessage(
                    self.playerchar).shop_message(), self._chat_id, self._player_id, self._keyboard)

    def shop(self, message=None):
        """
        Shop part
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(StatusMessage(self.playerchar).shop_message(), self._chat_id, self._player_id, self._keyboard)
        elif message != 'Exit':
            if message == 'Restore HP':
                hp = int(self.playerchar.get_maxhp() -
                         self.playerchar.get_current_hp())
                if self.playerchar.get_gold() >= hp:
                    self.playerchar.set_gold(self.playerchar.get_gold() - hp)
                    self.playerchar.set_hp(self.playerchar.get_maxhp())
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Small Potion':
                if self.playerchar.get_gold() >= 10:
                    self.playerchar.set_gold(self.playerchar.get_gold() - 10)
                    self.playerchar.set_hp(self.playerchar.get_current_hp() + 10)
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Medium Potion':
                if self.playerchar.get_gold() >= 100:
                    self.playerchar.set_gold(self.playerchar.get_gold() - 100)
                    self.playerchar.set_hp(self.playerchar.get_current_hp() + 100)
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Attack Boost':
                if self.playerchar.get_gold() >= 1000:
                    self.playerchar.set_gold(self.playerchar.get_gold() - 1000)
                    self.playerchar.set_attack(self.playerchar._attack + 10)
                    self.enqueue_message(
                        'Attack Boosted', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message(
                        'Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Magic Boost':
                if self.playerchar.get_gold() >= 1000:
                    self.playerchar.set_gold(self.playerchar.get_gold() - 1000)
                    self.enqueue_message(
                        'MP Boosted', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message(
                        'Not enough gold', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(StatusMessage(self.playerchar).shop_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            self.set_state('Base')
            self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id, self._keyboard)

    def create_battle(self):
        """Creating the enemy list first time"""
        self.enemies = self.create_enemy_list(self.playerchar.get_lvl())  # creating enemy
        for target in self.enemies:  # sending info for all enemies
            self.enqueue_message(DialogMessage(
                'see_enemy_C', target).get_message(), self._chat_id, self._player_id, self._keyboard)
            self.send_stats(target)
        self.enqueue_message(DialogMessage('attack_enemy').get_message(
        ), self._chat_id, self._player_id, self._keyboard)  # prompting to attack

    def battle_choice(self, message):
        """
        Battle battle_choice part
        Fight or flight, battle() or base()
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command',
                                 self._chat_id, self._player_id)
            self.enqueue_message(DialogMessage(
                'attack_enemy').get_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            if message == 'Attack':
                self.set_state('Battle')
                self.battle()
            elif message == 'Retreat':
                self.set_state('Base')
                self.enqueue_message("You've lost half of your gold, while running away", self._chat_id, self._player_id, self._keyboard)
                self.playerchar.set_gold(self.playerchar.get_gold()/2)
                self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id, self._keyboard)

    def create_enemy_list(self, lvl):
        """
        Enemy spawn rules
        Returns list of enemies
        """
        enemy_list = []
        monster = (0, 10, 20)
        g_monster = (10, 20, 30)
        enemies_count = lvl // 10

        for step in g_monster:
            ind = g_monster.index(step)
            if lvl >= step and len(enemy_list) < enemies_count + 1:
                if self.roll(4 - ind):
                    enemy_list.append(GreaterMonster(lvl))

        for step in monster:
            ind = monster.index(step)
            if lvl >= step and len(enemy_list) < enemies_count + 1:
                if self.roll(4 - ind):
                    enemy_list.append(Monster(lvl))

        if len(enemy_list) <= enemies_count:
            enemy_list.append(Monster(lvl))
        return enemy_list

    def battle(self):
        """
        Battle part
        If character is not dead, leads to won_battle()
        """
        battle_log = ""  # creating battle log
        while self.playerchar.is_alive():
            for skill in self.playerchar.get_skills():
                skill.set_current_cd(skill.get_current_cd() - 1)
            if self.playerchar.is_skill_available():
                skill = self.playerchar.first_available_skill()
                battle_log += self.playerchar.use_attack_skill(
                    skill, next(enemy for enemy in self.enemies if enemy.is_alive()))
                skill.set_current_cd(skill.get_cooldown_timer())
            else:
                battle_log += self.playerchar.attack(
                    next(enemy for enemy in self.enemies if enemy.is_alive()))
            for enemy in self.enemies:
                if enemy.is_alive():
                    battle_log += enemy.attack(self.playerchar)
                    if not self.playerchar.is_alive():
                        battle_log += DialogMessage('won_C',
                                                    enemy).get_message()
                        self.enqueue_message(
                            battle_log, self._chat_id, self._player_id, self._keyboard)
                        self.enqueue_message(DialogMessage(
                            'dead').get_message(), self._chat_id, self._player_id, self._keyboard)
                        # user_list.pop(self._player_id['id'])  # deleting user character
                        self.enqueue_message(DialogMessage(
                            'end_game').get_message(), self._chat_id, self._player_id, self._keyboard)
                        # this needs to be reworked
                        self.enqueue_message(
                            'Ready Player One', self._chat_id, self._player_id, self._keyboard)
                        self.enqueue_message(DialogMessage(
                            'start_game').get_message(), self._chat_id, self._player_id, self._keyboard)
                        self.set_state('Game Start')
                        # this needs to be reworked
                        break
            if all(not enemy.is_alive() for enemy in self.enemies):
                battle_log += DialogMessage('won_C',
                                            self.playerchar).get_message()
                self.enqueue_message(
                    battle_log, self._chat_id, self._player_id, self._keyboard)
                self.set_state('Battle Won')
                self.won_battle(self.enemies)
                for skill in self.playerchar.get_skills():
                    skill.set_current_cd(0)
                self.enemies = []  # deleting enemies
                break

    def won_battle(self, enemies):
        """
        After battle is won, hero gets his reward
        """
        for enemy in enemies:
            is_lvlup = self.playerchar.add_exp(enemy.get_maxhp())
            if is_lvlup:
                self.enqueue_message(is_lvlup, self._chat_id, self._player_id, self._keyboard)
            self.playerchar.set_gold(
                self.playerchar.get_gold() + int(enemy.get_attack()))  # gold drop
        self.check_drop(enemies)  # checking for item drop

    def check_drop(self, enemies):
        """
        Rolling for items and applying them to the character
        """
        # healing potion in a dire need of rewrite
        if random.randint(1, 7) % 6 == 0:
            hp = 'Healing Potion'
            item_healing = random.randint(10, int(enemies[0].get_maxhp()))
            self.enqueue_message(f"You found a *{hp}*!\n" +
                                 DialogMessage(
                                     'healed_CA', self.playerchar, item_healing).get_message(),
                                 self._chat_id, self._player_id)
            self.playerchar.set_hp(
                self.playerchar.get_current_hp() + item_healing)

        #   Lazy copypaste 2 lines at a time #

        def rare_drop(chance):
            """
            Rare drop roll method
            Adds drop to item_drop if chance is succesfull
            """
            if random.random() < chance:
                self.item_drop.append(RareItem(self.playerchar.get_lvl()))

        def common_drop(chance):
            """
            Common drop roll method
            Adds drop to item_drop if chance is succesfull
            """
            if random.random() < chance:
                self.item_drop.append(CommonItem(self.playerchar.get_lvl()))

        self.item_drop = []

        for enemy in enemies:
            enemy_score = enemy.get_maxhp() + enemy.get_attack()
            if enemy_score > 200:
                rare_drop(0.8)
            elif enemy_score > 150:
                rare_drop(0.5)
            elif enemy_score > 100:
                common_drop(1)
            elif enemy_score > 50:
                common_drop(0.8)
            else:
                common_drop(0.5)
        for item in self.item_drop:
            if item:
                playeritem = self.playerchar.get_inventory()[item.get_type()]
                if playeritem:
                    if item.get_bonus_attack() - playeritem.get_bonus_attack() <= 0 and \
                            item.get_bonus_hp() - playeritem.get_bonus_hp() <= 0 and \
                            item.get_bonus_mp() - playeritem.get_bonus_mp() <= 0 and \
                            item.get_bonus_defence() - playeritem.get_bonus_defence() <= 0:
                        self.item_drop.remove(item)
            else:
                self.item_drop.remove(item)

        if not self.item_drop:
            self.set_state('Base')
            self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            self.set_state('Item Choice')
            self.process_drop()

    def process_drop(self):
        """
        Processing all the drops, and prompting to choose equip item or not
        """
        self.item = self.item_drop[0]
        self.enqueue_message(DialogMessage('found_item_I', self.item).get_message(
        ) + "\n" + self.item.get_stats(), self._chat_id, self._player_id, self._keyboard)
        if self.playerchar.get_inventory()[self.item.get_type()]:
            playeritem = self.playerchar.get_inventory()[self.item.get_type()]
            self.enqueue_message(
                f"Comparing to your *{playeritem.get_full_name()}*:", self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(self.item.get_compare_stats(
                playeritem), self._chat_id, self._player_id, self._keyboard)
        self.enqueue_message(DialogMessage(
            'equip_item').get_message(), self._chat_id, self._player_id, self._keyboard)
        self.item_drop.pop(0)  # deleting first available item

    def item_choice(self, message):
        """
        Player battle_choice of equipping the item
        None is a dirty hack and I am not proud
        """
        if message not in self.get_state_input():
            self.enqueue_message('Please input correct command',
                                 self._chat_id, self._player_id)
            self.enqueue_message(DialogMessage(
                'equip_item').get_message(), self._chat_id, self._player_id, self._keyboard)
        else:
            if message == 'Equip':  # adds item to playerchar inventory
                self.playerchar.add_item(self.item)
                self.item = None
                self.send_inventory(self.playerchar)
                self.send_stats(self.playerchar)
            if self.item_drop != []:
                self.process_drop()
            else:
                self.set_state('Base')
                self.enqueue_message(DialogMessage(
                    'base').get_message(), self._chat_id, self._player_id, self._keyboard)


# TODO: pseudorandom
# TODO enemies: Dark Shadow
# TODO playerclass: Druid
# TODO: item sets
# TODO: initiative

class GameManager():
    """Holds games for all players, rutes and manages them"""

    def __init__(self, redis_save=True):
        if redis_save:
            from save import RedisConnection, REDIS_URL
            self.redis = RedisConnection(REDIS_URL)
            self.user_list = self.redis.get_all_games()
        else:
            self.user_list = {}
        self.redis_save = redis_save
        self.commands_out_game = {'/start': self.start_new_game}
        self.commands_in_game = {'/restart': self.restart_game}

    def merge_messages(self, messages):
        """
        Takes a list of messages
        Merges every subsequent message to one player, into bigger message
        """
        from itertools import groupby
        result = []
        separator = "\n\n"
        for key, group in groupby(messages, lambda x: x.chat_id):
            res = ""
            keyboard = None
            for message in group:
                if res:
                    res += separator + message.text
                else:
                    res += message.text
                if message.keyboard:
                    keyboard = message.keyboard
            result.append(OutMessage(res, key, key, keyboard))
        return result

    def start_new_game(self, chat_id, player_id):
        """Starts a new game, and returns appropriate messages"""
        self.user_list[player_id] = Game(chat_id, player_id)
        return [OutMessage(
            'Ready Player One', chat_id, player_id),
            OutMessage(DialogMessage(
                'start_game').get_message(), chat_id, player_id)]

    def restart_game(self, chat_id, player_id):
        """Restarts a game"""
        self.user_list.pop(player_id)
        return [OutMessage('Game reset', chat_id, player_id)]

    def process_out_game_commands(self, chat_id, player_id, content):
        """Processes all the commands outside of game"""
        if content in self.commands_out_game.keys():
            return self.commands_out_game[content](chat_id, player_id)
        else: 
            return self.invalid_input(chat_id, player_id)

    def process_in_game_commands(self, chat_id, player_id, content):
        "Process all the ingame commands"
        if content in self.commands_in_game.keys():
            return self.commands_in_game[content](chat_id, player_id)
        else: 
            return []

    def process_commands(self, chat_id, player_id, content):
        """Processes all the commands"""
        if player_id in self.user_list.keys():
            return self.process_in_game_commands(chat_id, player_id, content)
        else:
            return self.process_out_game_commands(chat_id, player_id, content)

    def get_all_commands(self):
        """Returns all avaliable commands"""
        return list(self.commands_out_game.keys())+list(self.commands_in_game.keys())

    def invalid_input(self, chat_id, player_id):
        return [OutMessage(
            'Type /start to enter the game', chat_id, player_id)]

    def generate_replays(self, update):
        messages_to_send = []
        try:
            for msg in update:
                new_message = Message(msg['message'])
                if new_message.get_type() != 'text':
                    pass
                else:
                    user = new_message.get_user_id()
                    chat_id = new_message.get_chat_id()
                    content = new_message.get_content()
                    player_id = user["id"]
                    if content in self.get_all_commands(): # commands
                        messages_to_send += self.process_commands(chat_id, player_id, content)
                    elif player_id in self.user_list.keys(): # game
                        player_game = self.user_list[player_id]
                        messages_to_send += player_game.process_incoming_message(
                            content)
                        if self.redis_save:
                            self.redis.save_game(chat_id, player_game)
                    else: # invalid input
                        messages_to_send += self.invalid_input(chat_id, player_id)
        except:
            print("Something went wrong")
            print("*"*50)
            traceback.print_exc()
            print("*"*50)
        return self.merge_messages(messages_to_send)


def main():
    dispatcher = BotHandler(TOKEN)
    game_manager = GameManager()

    while True:
        update = dispatcher.get_update()
        replays = game_manager.generate_replays(update)
        dispatcher.send_messages(replays)


if __name__ == '__main__':
    main()
