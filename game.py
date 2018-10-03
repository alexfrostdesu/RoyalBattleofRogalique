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

    def game_start(self, message):
        """
        Character selection state
        Intended for single use
        """
        # global playerchar
        if message not in ['Mage', 'Warrior', 'Rogue']:
            dispatcher.send_message('Please input correct class name', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('start_game').get_message(), self._chat_id, self._player_id)
        else:
            self.playerchar = eval("{}()".format(message))
            player_stats = StatusMessage(self.playerchar).stats_message()
            player_inventory = StatusMessage(self.playerchar).inventory_message()
            dispatcher.send_message(player_stats, self._chat_id, self._player_id)
            dispatcher.send_message(player_inventory, self._chat_id, self._player_id)
            self.set_state('Base')
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)

    def base(self, message):
        """
        Base state
        Adventure starts from here
        Inventory, status, shop
        """
        if message not in ['Y', 'S', 'I']:
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
        else:
            if message == 'S':
                player_stats = StatusMessage(self.playerchar).stats_message()
                dispatcher.send_message(player_stats, self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            elif message == 'I':
                player_inventory = StatusMessage(self.playerchar).inventory_message()
                dispatcher.send_message(player_inventory, self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            elif message == 'Y':
                self.enemy = Monster(self.playerchar.get_lvl())
                dispatcher.send_message(DialogMessage('see_enemy_C', self.enemy).get_message(), self._chat_id, self._player_id)
                enemy_stats = StatusMessage(self.enemy).stats_message()
                dispatcher.send_message(enemy_stats, self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('attack_enemy').get_message(), self._chat_id, self._player_id)
                self.set_state('Battle Choice')

    def choice(self, message):
        """
        Battle choice part
        Fight or flight, battle() or base()
        """
        if message not in ['Y', 'N']:
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('attack_enemy').get_message(), self._chat_id, self._player_id)
        else:
            if message == 'Y':
                self.set_state('Battle')
                dispatcher.send_message('You are in Battle right now', self._chat_id, self._player_id)
                self.battle()
            elif message == 'N':
                self.set_state('Base')
                dispatcher.send_message('Returning to base', self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)

    def battle(self):
        """
        Battle part
        If character is not dead, leads to won_battle()
        """
        battle_log = ""
        while self.playerchar.is_alive() and self.enemy.is_alive():
            battle_log += self.playerchar.attack(self.enemy)
            if not self.enemy.is_alive():
                battle_log += DialogMessage('won_C', self.playerchar).get_message()
                dispatcher.send_message(battle_log, self._chat_id, self._player_id)
                self.set_state('Battle Won')
                self.won_battle(self.enemy)
                self.enemy = None # deleting enemy
                break
            battle_log += self.enemy.attack(self.playerchar)
            if not self.playerchar.is_alive():
                battle_log += DialogMessage('won_C', self.enemy).get_message()
                dispatcher.send_message(battle_log, self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('dead').get_message(), self._chat_id, self._player_id)
                dispatcher.send_message(DialogMessage('end_game').get_message(), self._chat_id, self._player_id)
                user_list.pop(self._player_id['id'])
                break

    def won_battle(self, enemy):
        dispatcher.send_message(self.playerchar.add_exp(enemy.get_maxhp()), self._chat_id, self._player_id)
        self.item_drop(enemy)
        # player_stats = StatusMessage(self.playerchar).stats_message()
        # dispatcher.send_message(player_stats, self._chat_id, self._player_id)
        # self.set_state('Base')
        # dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)

    def item_drop(self, enemy):
        if random.randint(1, 6) % 3 == 0:
            item = 'Healing Potion'
            item_healing = random.randint(10, enemy.get_maxhp())
            dispatcher.send_message(f"You found a {item}!\n" + DialogMessage('healed_CA', self.playerchar, item_healing).get_message(), self._chat_id, self._player_id)
            self.playerchar.set_hp(self.playerchar.get_current_hp() + item_healing)

        enemy_score = enemy.get_maxhp() + enemy.get_attack()

        def rare_drop(chance):
            if random.random() < chance:
                return RareItem(self.playerchar.get_lvl())

        def common_drop(chance):
            if random.random() < chance:
                return CommonItem(self.playerchar.get_lvl())

        def check_drop(item_list):
            for item in item_droplist:
                if item:
                    self.item = item
                    dispatcher.send_message(DialogMessage('found_item_I', item).get_message() + "\n" + item.get_stats(), self._chat_id, self._player_id)
                    if self.playerchar.get_inventory()[item.get_type()]:
                        playeritem = self.playerchar.get_inventory()[item.get_type()]
                        dispatcher.send_message(f"Comparing to your *{playeritem.get_full_name()}*:", self._chat_id, self._player_id)
                        dispatcher.send_message(item.get_compare_stats(playeritem), self._chat_id, self._player_id)
                    dispatcher.send_message(DialogMessage('equip_item').get_message(), self._chat_id, self._player_id)
                    self.set_state('Item Choice')

        if enemy_score > 200:
            item_droplist = [rare_drop(1), common_drop(0.2)]
            check_drop(item_droplist)
        elif enemy_score > 100:
            item_droplist = [rare_drop(1), common_drop(0.2)]
            check_drop(item_droplist)
        elif enemy_score > 50:
            item_droplist = [rare_drop(1), common_drop(0.3)]
            check_drop(item_droplist)
        else:
            item_droplist = [common_drop(1)]
            check_drop(item_droplist)

    def item_choice(self, message):
        if message not in ['Y', 'N', None]:
            dispatcher.send_message('Please input correct command', self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('equip_item').get_message(), self._chat_id, self._player_id)
        elif message is None:
            dispatcher.send_message(DialogMessage('equip_item').get_message(), self._chat_id, self._player_id)
        elif message == 'Y':
            self.playerchar.add_item(self.item)
            self.item = None
            player_inventory = StatusMessage(self.playerchar).inventory_message()
            dispatcher.send_message(player_inventory, self._chat_id, self._player_id)
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            self.set_state('Base')
        elif message == 'N':
            self.item = None
            dispatcher.send_message(DialogMessage('base').get_message(), self._chat_id, self._player_id)
            self.set_state('Base')


        # while playerchar.is_alive():
        #     dispatcher.send_message(DialogMessage('find_enemy').get_message(), session, player)
        #     player_input = Message(dispatcher.wait_message()).get_content()
        #     if player_input == 'I':
        #         dispatcher.send_message(playerchar._get_all_items(), session, player)
        #         Game.adventure(playerchar)
        #         break
        #     elif player_input == 'N':
        #         dispatcher.send_message(DialogMessage('end_game').get_message(), session, player)
        #         break
        #     else:
        #         if random.random() < 0.6:
        #             if random.random() < 0.3 and playerchar.get_lvl() >= 4:
        #                 enemy = GreaterMonster(playerchar.get_lvl())
        #             else:
        #                 enemy = Monster(playerchar.get_lvl())
        #             enemy_prompt = DialogMessage('see_enemy_C', enemy).get_message() + "\n" \
        #                            + enemy.get_stats() + "\n"
        #             dispatcher.send_message(enemy_prompt, session, player)
        #             dispatcher.send_message(DialogMessage('attack_enemy').get_message(), session, player)
        #             player_input = Message(dispatcher.wait_message()).get_content()
        #             if player_input == 'Y':
        #                 Game.battle_encounter(playerchar, enemy, True)
        #             else:
        #                 Game.adventure(playerchar)
        #                 break
        #
        #         else:
        #             enemy = Monster(playerchar.get_lvl())
        #             enemy_prompt = DialogMessage('enemy_attack_C', enemy).get_message() + "\n" \
        #                            + enemy.get_stats() + "\n"
        #             dispatcher.send_message(enemy_prompt, session, player)
        #             Game.battle_encounter(playerchar, enemy, False)

    @staticmethod
    def battle_until_death(attacker, defender):
        """
        Takes attacker's and defender's characters and battles them until one of them is dead
        """
        battle_log = ""
        while attacker.is_alive() and defender.is_alive():
            battle_log += attacker.attack(defender)
            if not defender.is_alive():
                battle_log += DialogMessage('won_C', attacker).get_message()
                dispatcher.send_message(battle_log, session, player)
                break
            battle_log += defender.attack(attacker)
            if not attacker.is_alive():
                battle_log += DialogMessage('won_C', defender).get_message()
                dispatcher.send_message(battle_log, session, player)
                break

    # @staticmethod
    # def item_drop(enemy):
    #
    #     if random.randint(1, 6) % 3 == 0:
    #         item = 'Healing Potion'
    #         item_healing = random.randint(10, 30)
    #         dispatcher.send_message(f"You found a {item}!\n" + DialogMessage('healed_CA', playerchar, item_healing).get_message(), session, player)
    #         playerchar.set_hp(round(playerchar.get_current_hp() + item_healing))
    #
    #     enemy_score = enemy.get_maxhp() + enemy.get_attack()
    #
    #     def rare_drop(chance):
    #         if random.random() < chance:
    #             return RareItem(playerchar.get_lvl())
    #
    #     def common_drop(chance):
    #         if random.random() < chance:
    #             return CommonItem(playerchar.get_lvl())
    #
    #     def check_drop(item_list):
    #         for item in item_droplist:
    #             if item:
    #                 dispatcher.send_message(DialogMessage('found_item_I', item).get_message() + "\n" + item.get_stats(), session, player)
    #
    #                 if playerchar.get_inventory()[item.get_type()]:
    #                     playeritem = playerchar.get_inventory()[item.get_type()]
    #                     dispatcher.send_message(
    #                         f"Comparing to your {playeritem.get_full_name()}:\n" + item.get_compare_stats(playeritem),
    #                         session, player)
    #
    #                 dispatcher.send_message("Would you like to equip item? (Y/N)", session, player)
    #                 player_input = Message(dispatcher.wait_message()).get_content()
    #                 if player_input == 'Y':
    #                     playerchar.add_item(item)
    #
    #     if enemy_score > 200:
    #         item_droplist = [rare_drop(0.6), common_drop(0.2)]
    #         check_drop(item_droplist)
    #
    #     if enemy_score > 100:
    #         item_droplist = [rare_drop(0.6), common_drop(0.2)]
    #         check_drop(item_droplist)
    #
    #     if enemy_score > 50:
    #         item_droplist = [rare_drop(0.2), common_drop(0.3)]
    #         check_drop(item_droplist)
    #     else:
    #         item_droplist = [common_drop(0.3)]
    #         check_drop(item_droplist)

    @staticmethod
    def battle_encounter(playerchar, enemy, first_attack=False):
        """
        Takes playerchar's and enemy's characters and battles them until one of them is dead
        First attack determined by first_attack
        Grants player with random item and exp from monster
        """
        if first_attack:
            Game.battle_until_death(playerchar, enemy)
        else:
            Game.battle_until_death(enemy, playerchar)
        if not playerchar.is_alive():
            dispatcher.send_message(DialogMessage('dead').get_message(), session, player)
            dispatcher.send_message(DialogMessage('end_game').get_message(), session, player)
        else:
            Game.item_drop(enemy)
            dispatcher.send_message(playerchar.add_exp(enemy.get_maxhp()), session, player)
            player_stats = DialogMessage('stats').get_message() + "\n" + playerchar.get_stats() + "\n" + playerchar.get_exp_lvl()
            dispatcher.send_message(player_stats, session, player)




# TODO mp -> mf for skills
# TODO skills: Mage Fireball
# TODO skills: Rogue Confusion
# TODO enemies: Dark Shadow
# TODO game: save state
# TODO game: console choice?

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
                        dispatcher.send_message('Game reseted', chat_id, player_id)
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

        # if msg.get_type() != 'text':
        #     dispatcher.send_message('Type /start to enter the game', msg.get_chat_id(), msg.get_user_id())
        #     time.sleep(0.5)
        #     pass
        # else:
        #     if msg.get_content() == '/start':
        #         dispatcher.send_message('Ready Player One', msg.get_chat_id(), msg.get_user_id())
        #         global player
        #         player = msg.get_user_id()
        #         time.sleep(1)
        #         dispatcher.send_message(DialogMessage('start_game').get_message(), msg.get_chat_id(), msg.get_user_id())
        #         Game.game_start()
        #     else:
        #         dispatcher.send_message('Type /start to enter the game', msg.get_chat_id(), msg.get_user_id())
        #         time.sleep(0.5)
        #         pass

if __name__ == '__main__':
    main()
