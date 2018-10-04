from classes import *
from events import DialogMessage, StatusMessage
from bot_handler import BotHandler, Message
import random
import time
import os



TOKEN = os.environ["TOKEN"]


class Game:
    def __init__(self, chat_id, player_id):
        self._player_id = player_id
        self._chat_id = chat_id
        self._game_state = 'Game Start'
        dispatcher.send_message(DialogMessage('start_game').get_message(), self._chat_id, self._player_id)

    def check_state(self):
        """
        Get current game state
        """
        return self._game_state

    def set_state(self, state):
        """
        Setting game state to another value
        """
        self._game_state = state

    def get_playerchar(self):
        """
        Get current game player character
        """
        return self.playerchar

#   Lazy copypast 2 lines at a time #

    def send_stats(self, char):
        """
        Shows the stats message
        """
        _stats = StatusMessage(char).stats_message()
        dispatcher.send_message(_stats, self._chat_id, self._player_id)

    def send_inventory(self, char):
        """
        Shows the inventory message
        """
        _inventory = StatusMessage(char).inventory_message()
        dispatcher.send_message(_inventory, self._chat_id, self._player_id)

    def game_start(self, message):
        """
        Character selection state
        Intended for single use
        """
        if message not in ['Mage', 'Warrior', 'Rogue']:  # standard check for right input
            dispatcher.send_message('Please input correct class name', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('start_game').get_message(), self._chat_id, self._player_id)
        else:
            self.playerchar = eval("{}()".format(message))  # creating player character
            self.send_stats(self.playerchar)
            self.set_state('Base')
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)

    def base(self, message):
        """
        Base state
        Adventure starts from here
        Inventory, status, shop
        """
        if message not in ['Y', 'S', 'I']:  # standard check for right input
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
        else:
            if message == 'S':
                self.send_stats(self.playerchar)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            elif message == 'I':
                self.send_inventory(self.playerchar)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            elif message == 'Y':
                self.choice()
                self.set_state('Battle Choice')

    def choice(self, message=None):
        """
        Battle choice part
        Fight or flight, battle() or base()
        """
        if message is None:  # Creating the enemy list first time
            self.enemies = self.create_enemy_list(self.playerchar.get_lvl())  # creating enemy
            for target in self.enemies:  # sending info for all enemies
                dispatcher.send_message(DialogMessage('see_enemy_C', target).get_message(), self._chat_id, self._player_id)
                self.send_stats(target)
            dispatcher.send_message(DialogMessage('attack_enemy').get_message(), self._chat_id, self._player_id)  # prompting to attack
        elif message not in ['Y', 'N']:  # standard check for right input
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('attack_enemy').get_message(), self._chat_id, self._player_id)
        else:
            if message == 'Y':
                self.set_state('Battle')
                # dispatcher.send_message('You are in Battle right now', self._chat_id, self._player_id)
                self.battle()
            elif message == 'N':
                self.set_state('Base')
                dispatcher.send_message('Returning to base', self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)

    def create_enemy_list(self, lvl):
        """
        Enemy spawn rules
        Returns list
        """
        if lvl < 4:
            enemy_list = [Monster(lvl)]
        if 4 <= lvl < 7:
            roll = random.randint(1, 6)
            if roll % 3 == 0:
                enemy_list = [GreaterMonster(lvl)]
            else:
                enemy_list = [Monster(lvl)]
        if 7 <= lvl < 10:
            roll = random.randint(1, 6)
            if roll % 2 == 0:
                enemy_list = [GreaterMonster(lvl)]
            elif roll % 3 == 0:
                enemy_list = [GreaterMonster(lvl), Monster(lvl)]
            else:
                enemy_list = [Monster(lvl)]
        if lvl >= 10:
            roll = random.randint(1, 6)
            if roll % 6 == 0:
                enemy_list = [GreaterMonster(lvl), GreaterMonster(lvl)]
            if roll % 3 == 0:
                enemy_list = [GreaterMonster(lvl), Monster(lvl)]
            else:
                enemy_list = [Monster(lvl), Monster(lvl)]
        return enemy_list

    def battle(self):
        """
        Battle part
        If character is not dead, leads to won_battle()
        """
        battle_log = ""  # creating battle log
        while self.playerchar.is_alive():
            battle_log += self.playerchar.attack(next(enemy for enemy in self.enemies if enemy.is_alive()))
            for enemy in self.enemies:
                if enemy.is_alive():
                    battle_log += enemy.attack(self.playerchar)
                    if not self.playerchar.is_alive():
                        battle_log += DialogMessage('won_C', enemy).get_message()
                        dispatcher.send_message(battle_log, self._chat_id, self._player_id)
                        dispatcher.send_message(DialogMessage('dead').get_message(), self._chat_id, self._player_id)
                        dispatcher.send_message(DialogMessage('end_game').get_message(), self._chat_id, self._player_id)
                        user_list.pop(self._player_id['id'])  # deleting user character
                        break
            if all(not enemy.is_alive() for enemy in self.enemies):
                battle_log += DialogMessage('won_C', self.playerchar).get_message()
                dispatcher.send_message(battle_log, self._chat_id, self._player_id)
                self.set_state('Battle Won')
                self.won_battle(self.enemies)
                self.enemies = []  # deleting enemies
                break


    def won_battle(self, enemies):
        """
        After battle is won, hero gets his reward
        """
        for enemy in enemies:
            dispatcher.send_message(self.playerchar.add_exp(enemy.get_maxhp()), self._chat_id, self._player_id)
            self.item_drop(enemy)  # checking for item drop

    def item_drop(self, enemy):
        """
        Rolling for items and applying them to the character
        """
        if random.randint(1, 6) % 3 == 0:
            item = 'Healing Potion'
            item_healing = random.randint(10, int(enemy.get_maxhp()))
            dispatcher.send_message(f"You found a *{item}*!\n" + DialogMessage('healed_CA', self.playerchar, item_healing).get_message(), self._chat_id, self._player_id)
            self.playerchar.set_hp(self.playerchar.get_current_hp() + item_healing)

        enemy_score = enemy.get_maxhp() + enemy.get_attack()

        def rare_drop(chance):
            """
            Rare drop roll method
            Item or None
            """
            if random.random() < chance:
                return RareItem(self.playerchar.get_lvl())

        def common_drop(chance):
            """
            Common drop roll method
            Item or None
            """
            if random.random() < chance:
                return CommonItem(self.playerchar.get_lvl())

        def check_drop(item):
            """
            Checking drop and sending game to 'Item Choice' state
            """
            self.item = item
            dispatcher.send_message(DialogMessage('found_item_I', item).get_message() + "\n" + item.get_stats(), self._chat_id, self._player_id)
            if self.playerchar.get_inventory()[item.get_type()]:
                playeritem = self.playerchar.get_inventory()[item.get_type()]
                dispatcher.send_message(f"Comparing to your *{playeritem.get_full_name()}*:", self._chat_id, self._player_id)
                dispatcher.send_message(item.get_compare_stats(playeritem), self._chat_id, self._player_id)
            self.set_state('Item Choice')
            self.item_choice()


################################################
#        PODUMOI VOT TUT                       #
################################################

        if enemy_score > 200:
            item_droplist = [rare_drop(0.5)]
        elif enemy_score > 100:
            item_droplist = [rare_drop(0.3)]
        elif enemy_score > 50:
            item_droplist = [common_drop(0.5)]
        else:
            item_droplist = [common_drop(0.2)]

        if all(item is None for item in item_droplist):  # checks if there no items in drop
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            self.set_state('Base')
        else:
            for item in item_droplist:  # check out every item
                if item:
                    check_drop(item)

    def item_choice(self, message=None):
        """
        Player choice of equipping the item
        None is a dirty hack and I am not proud
        """
        if message not in ['Y', 'N', None]:
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('equip_item').get_message(), self._chat_id, self._player_id)
        elif message is None:  # dirty hack
            dispatcher.send_message(DialogMessage('equip_item').get_message(), self._chat_id, self._player_id)
        else:
            if message == 'Y':
                self.playerchar.add_item(self.item)
                self.item = None
                player_inventory = StatusMessage(self.playerchar).inventory_message()
                dispatcher.send_message(player_inventory, self._chat_id, self._player_id)
            elif message == 'N':  # y u no like muh item
                self.item = None
            self.send_stats(self.playerchar)
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            self.set_state('Base')


# TODO mp -> mf for skills
# TODO skills: Mage Fireball
# TODO skills: Rogue Confusion
# TODO enemies: Dark Shadow
# TODO: initiative
# TODO: skills as classes

def main():
    global dispatcher
    global user_list
    dispatcher = BotHandler(TOKEN)
    user_list = dict()
    while True:
        update = dispatcher.get_update()
        for msg in update:
            new_message = Message(msg['message'])
            if new_message.get_type() != 'text':
                pass
            else:
                player_id = new_message.get_user_id()
                chat_id = new_message.get_chat_id()
                content = new_message.get_content()
                if player_id['id'] not in user_list.keys() and content == '/start':
                    dispatcher.send_message('Ready Player One', chat_id, player_id)
                    player_game = Game(chat_id, player_id)
                    user_list[player_id['id']] = player_game
                elif player_id['id'] in user_list:
                    if new_message.get_content() == '/restart':
                        user_list.pop(player_id['id'])
                        dispatcher.send_message('Game reset', chat_id, player_id)
                    else:
                        player_game = user_list[player_id['id']]
                        game_state = player_game.check_state()
                        if game_state == 'Game Start':
                            player_game.game_start(content)
                        elif game_state == 'Base':
                            player_game.base(content)
                        elif game_state == 'Battle Choice':
                            player_game.choice(content)
                        elif game_state == 'Item Choice':
                            player_game.item_choice(content)
                        # dispatcher.send_message(game_state, chat_id, player_id)
                    # if goes here
                    # player_game.cont(Message(msg).get_content())
                else:
                    dispatcher.send_message('Type /start to enter the game', chat_id, player_id)


if __name__ == '__main__':
    main()
