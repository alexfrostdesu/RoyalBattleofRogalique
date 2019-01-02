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
        self._enemy = None
        self._boss = None
        self._chat_id = chat_id
        self._game_state = 'Game Start'
        self._message_send_list = []
        self._first_launch = True
        self._act = 1
        self._keyboard = json.dumps(
            {'keyboard': [self.get_state_input()], 'one_time_keyboard': False, 'resize_keyboard': True})

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
        _keyboard = []
        _buttons = self.get_state_input()
        if _buttons:
            length = len(_buttons)
            if length > 4:
                for i in range(length // 4):
                    _keyboard.append(_buttons[:4])
                    _buttons = _buttons[4:]
            _keyboard.append(_buttons)
        self._keyboard = json.dumps({'keyboard': _keyboard, 'one_time_keyboard': False, 'resize_keyboard': True})

    @functools.lru_cache(10)
    def get_game_states(self):
        return {'Game Start': {"func": self.game_start,
                               "input": ['Mage', 'Warrior', 'Rogue']},
                'Base': {"func": self.base,
                         "input": ['Shop', 'Stats', 'Skills', 'Inventory', 'Check Boss', 'Find Monsters']},
                'Battle': {"func": self.battle,
                           "input": None},
                'Battle Won': {"func": self.won_battle,
                               "input": None},
                'Enemy Choice': {"func": self.enemy_choice,
                                 "input": ['Attack', 'Retreat']},
                'Item Choice': {"func": self.item_choice,
                                "input": ['Equip', 'Discard']},
                'Shop': {"func": self.shop,
                         "input": ['Restore HP', 'Small Potion', 'Medium Potion', 'Attack Boost', 'Magic Boost',
                                   'Exit']},
                'Boss Choice': {"func": self.boss_choice,
                                "input": ['Attack Boss', 'Return to base']}}

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
        processes based on a game state
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

    def send_skills(self, char):
        """
        Shows the skills message
        """
        _skills = StatusMessage(char).skills_message()
        self.enqueue_message(_skills, self._chat_id, self._player_id)

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
        # 1 act -- GreaterMonster (Monster)
        # 2 act -- ChampionMonster (Monster, GreaterMonster)
        # 3 act -- Summoner (GreaterMonster, ChampionMonster)
        # 4 act -- DarkShadow (ChampionMonster, Summoner)
        if self._boss is None:
            self.create_boss(self._act)
        if self._enemy is None:
            self.create_enemy(self._act)
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
            elif message == 'Skills':
                self.send_skills(self.playerchar)
                self.enqueue_message(DialogMessage(
                    'base').get_message(), self._chat_id, self._player_id, self._keyboard)
            elif message == 'Check Boss':
                self.set_state('Boss Choice')
                self.check_enemy(self._boss)
            elif message == 'Find Monsters':
                self.set_state('Enemy Choice')
                self.check_enemy(self._enemy)
            elif message == 'Shop':
                self.set_state('Shop')
                self.enqueue_message(StatusMessage(
                    self.playerchar).shop_message(), self._chat_id, self._player_id, self._keyboard)

        # 1 act -- GreaterMonster (Monster)
        # 2 act -- ChampionMonster (Monster, GreaterMonster)
        # 3 act -- Summoner (GreaterMonster, ChampionMonster)
        # 4 act -- DarkShadow (ChampionMonster, Summoner)

    def create_boss(self, act):
        """
        Creating act boss enemy
        """
        slot_list = ['Helm', 'Armour', 'Boots', 'Ring', 'Weapon']
        act_list = {1: {'Boss': GreaterMonster,
                        'Items': [RareItem(act + 1, slot) for slot in slot_list] + [UniqueItem(act + 1)]},
                    2: {'Boss': ChampionMonster,
                        'Items': [RareItem(act + 1, slot) for slot in slot_list] + [UniqueItem(act + 1)]},
                    3: {'Boss': Summoner,
                        'Items': [RareItem(act + 1, slot) for slot in slot_list] + [UniqueItem(act + 1)]},
                    #4: DarkShadow
                    }
        if act > max(act_list.keys()):
            act = max(act_list.keys())  # don't forget to change that!
        boss = act_list[act]['Boss'](act + 1)
        for item in act_list[act]['Items']:
            boss.add_item(item)
        boss.update_skills()
        self._boss = {'Enemy': boss, 'Type': 'Boss'}

    def create_enemy(self, act):
        """
        Enemy spawn rules
        """
        lvl = self.playerchar.get_lvl()
        slot_list = ['Helm', 'Armour', 'Boots', 'Ring', 'Weapon']
        act_list = {1: [{'Enemy': Monster,
                        'Items': [CommonItem(lvl, slot) for slot in random.sample(slot_list, 1)]}],
                    2: [{'Enemy': Monster,
                        'Items': [CommonItem(lvl, slot) for slot in random.sample(slot_list, 2)]},
                        {'Enemy': GreaterMonster,
                         'Items': [CommonItem(lvl, slot) for slot in random.sample(slot_list, 3)] + [RareItem(lvl, slot) for slot in random.sample(slot_list, 1)]}
                        ],
                    3: [{'Enemy': GreaterMonster,
                         'Items': [RareItem(lvl, slot) for slot in random.sample(slot_list, 4)]},
                        {'Enemy': ChampionMonster,
                         'Items': [RareItem(lvl, slot) for slot in random.sample(slot_list, 1)]}
                        ],
                    4: [{'Enemy': GreaterMonster,
                         'Items': [RareItem(lvl, slot) for slot in random.sample(slot_list, 5)]},
                        {'Enemy': ChampionMonster,
                         'Items': [RareItem(lvl, slot) for slot in random.sample(slot_list, 5)]},
                        {'Enemy': Summoner,
                         'Items': [RareItem(lvl, slot) for slot in random.sample(slot_list, 5)]}
                        ]
                    #5: DarkShadow
                    }
        if act > max(act_list.keys()):
            act = max(act_list.keys())  # don't forget to change that!
        enemy_dict = random.choice(act_list[act])
        enemy = enemy_dict['Enemy'](act + lvl)
        for item in enemy_dict['Items']:
            enemy.add_item(item)
        enemy.update_skills()
        self._enemy = {'Enemy': enemy, 'Type': 'Normal'}

    def boss_choice(self, message):
        """
        Battle enemy_choice part
        Fight or flight, battle() or base()
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command',
                                 self._chat_id, self._player_id)
            self.enqueue_message(DialogMessage('attack_enemy').get_message(),
                                 self._chat_id, self._player_id, self._keyboard)
        else:
            if message == 'Attack Boss':
                self.set_state('Battle')
                self.battle(self._boss)
            elif message == 'Return to base':
                self.set_state('Base')
                self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id,
                                     self._keyboard)

    def enemy_choice(self, message):
        """
        Battle enemy_choice part
        Fight or flight, battle() or base()
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command',
                                 self._chat_id, self._player_id)
            self.enqueue_message(DialogMessage('attack_enemy').get_message(),
                                 self._chat_id, self._player_id, self._keyboard)
        else:
            if message == 'Attack':
                self.set_state('Battle')
                self.battle(self._enemy)
            elif message == 'Retreat':
                self.set_state('Base')
                self.enqueue_message("You've lost half of your gold, while running away", self._chat_id,
                                     self._player_id, self._keyboard)
                self.playerchar.set_gold(self.playerchar.get_gold() / 2)
                self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id,
                                     self._keyboard)

    def check_enemy(self, enemy):
        """
        Sending message about the enemy
        """
        enemy_char = enemy['Enemy']
        enemy_type = enemy['Type']
        message_list = {'Normal': DialogMessage('see_enemy_C', {'char': enemy_char.get_class()}).get_message(),
                        'Boss': 'You approach the boss of this act:'}
        self.enqueue_message(message_list[enemy_type],
                             self._chat_id, self._player_id, self._keyboard)
        self.send_stats(enemy_char)
        if enemy_char.get_summons():
            self.enqueue_message("Enemy summons:",
                                 self._chat_id, self._player_id, self._keyboard)
            for summon in enemy_char.get_summons():
                self.send_stats(summon)
        self.enqueue_message(DialogMessage('attack_enemy').get_message(),
                             self._chat_id, self._player_id, self._keyboard)  # prompting to attack

    def battle(self, enemy):
        """
        Battle part
        If character is not dead, leads to won_battle()
        """
        battle_log = ""  # creating battle log
        enemy_char = enemy['Enemy']
        player_chars = [self.playerchar] + self.playerchar.get_summons()
        enemies = [enemy_char] + enemy_char.get_summons()
        while self.playerchar.is_alive():
            for char in player_chars:
                if char.is_alive():
                    battle_log += char.attack(enemy_char)
            if not enemy_char.is_alive():
                battle_log += DialogMessage('won_C',
                                            {'char': self.playerchar.get_class()}).get_message()
                self.enqueue_message(
                    battle_log, self._chat_id, self._player_id, self._keyboard)
                for skill in self.playerchar.get_attack_skills():
                    skill.set_current_cd(0)
                self.won_battle(enemy_char)
                if enemy['Type'] == 'Boss':
                    self._act += 1
                    self._boss = None
                elif enemy['Type'] == 'Normal':
                    self._enemy = None
                break
            for char in enemies:
                if char.is_alive():
                    battle_log += char.attack(self.playerchar)
            if not self.playerchar.is_alive():
                battle_log += DialogMessage('won_C', {'char': enemy_char.get_class()}).get_message() + '\n'
                battle_log += DialogMessage('dead').get_message() + '\n'
                battle_log += DialogMessage('end_game').get_message() + '\n'
                self.enqueue_message(
                    battle_log, self._chat_id, self._player_id, self._keyboard)
                # user_list.pop(self._player_id['id'])  # deleting user character
                self._enemy = self._boss = None
                self._act = 1
                # this needs to be reworked
                self.set_state('Game Start')
                self.enqueue_message(
                    'Ready Player One', self._chat_id, self._player_id, self._keyboard)
                self.enqueue_message(DialogMessage(
                    'start_game').get_message(), self._chat_id, self._player_id, self._keyboard)
                break

    def won_battle(self, enemy):
        """
        After battle is won, hero gets his reward
        """
        is_lvlup = self.playerchar.add_exp(enemy.get_maxhp())
        if is_lvlup:
            self.enqueue_message(is_lvlup, self._chat_id, self._player_id, self._keyboard)
        self.playerchar.set_gold(
                self.playerchar.get_gold() + int(enemy.get_attack()))  # gold drop
        self.check_drop(enemy)  # checking for item drop

    def check_drop(self, enemy):
        """
        Rolling for items and applying them to the character
        """
        # healing potion in a dire need of rewrite
        if self.roll(5):
            hp = 'Healing Potion'
            item_healing = random.randint(10, int(enemy.get_maxhp()))
            self.enqueue_message(f"You found a *{hp}*!\n" +
                                 DialogMessage(
                                     'healed_CA',
                                     {'char': self.playerchar.get_class(), 'amount': item_healing}).get_message(),
                                 self._chat_id, self._player_id)
            self.playerchar.heal(item_healing)

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
        self.enqueue_message(DialogMessage('found_item_I', {'item': self.item.get_name()}).get_message(
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
        Player enemy_choice of equipping the item
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

    def shop(self, message=None):
        """
        Shop part
        """
        if message not in self.get_state_input():  # standard check for right input
            self.enqueue_message('Please input correct command', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(StatusMessage(self.playerchar).shop_message(), self._chat_id, self._player_id,
                                 self._keyboard)
        elif message != 'Exit':
            if message == 'Restore HP':
                hp = int(self.playerchar.get_maxhp() -
                         self.playerchar.get_current_hp())
                if self.playerchar.get_gold() >= hp:
                    self.playerchar.spend_gold(hp)
                    self.playerchar.set_hp(self.playerchar.get_maxhp())
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Small Potion':
                if self.playerchar.get_gold() >= 10:
                    self.playerchar.spend_gold(10)
                    self.playerchar.set_hp(self.playerchar.get_current_hp() + 10)
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Medium Potion':
                if self.playerchar.get_gold() >= 100:
                    self.playerchar.spend_gold(100)
                    self.playerchar.set_hp(self.playerchar.get_current_hp() + 100)
                    self.enqueue_message(
                        'HP restored', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message('Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Attack Boost':
                if self.playerchar.get_gold() >= 1000:
                    self.playerchar.spend_gold(1000)
                    self.playerchar.set_attack(self.playerchar._attack + 10)
                    self.enqueue_message(
                        'Attack Boosted', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message(
                        'Not enough gold', self._chat_id, self._player_id, self._keyboard)
            if message == 'Magic Boost':
                if self.playerchar.get_gold() >= 1000:
                    self.playerchar.spend_gold(1000)
                    self.enqueue_message(
                        'MP Boosted', self._chat_id, self._player_id, self._keyboard)
                    self.send_stats(self.playerchar)
                else:
                    self.enqueue_message(
                        'Not enough gold', self._chat_id, self._player_id, self._keyboard)
            self.enqueue_message(StatusMessage(self.playerchar).shop_message(), self._chat_id, self._player_id,
                                 self._keyboard)
        else:
            self.set_state('Base')
            self.enqueue_message(DialogMessage('base').get_message(), self._chat_id, self._player_id, self._keyboard)


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
        print("before merge", messages)
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
        print("after merge", result)
        return result

    def start_new_game(self, chat_id, player_id):
        """Starts a new game, and returns appropriate messages"""
        self.user_list[player_id] = Game(chat_id, player_id)
        keyboard = json.dumps(
            {'keyboard': [['Mage', 'Warrior', 'Rogue']], 'one_time_keyboard': False, 'resize_keyboard': True})
        return [OutMessage(
            'Ready Player One', chat_id, player_id),
            OutMessage(DialogMessage(
                'start_game').get_message(), chat_id, player_id, keyboard)]

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
        return list(self.commands_out_game.keys()) + list(self.commands_in_game.keys())

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
                    if content in self.get_all_commands():  # commands
                        messages_to_send += self.process_commands(chat_id, player_id, content)
                    elif player_id in self.user_list.keys():  # game
                        player_game = self.user_list[player_id]
                        messages_to_send += player_game.process_incoming_message(
                            content)
                        if self.redis_save:
                            self.redis.save_game(chat_id, player_game)
                    else:  # invalid input
                        messages_to_send += self.invalid_input(chat_id, player_id)
        except:
            print("Something went wrong")
            print("*" * 50)
            traceback.print_exc()
            print("*" * 50)
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
