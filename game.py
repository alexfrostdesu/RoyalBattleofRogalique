from classes import *
from events import DialogMessage
from bot_handler import BotHandler, Message
import random
import time
import os

TOKEN = os.environ["TOKEN"]

class Game:
    @staticmethod
    def game_start():
        """
        Character selection string
        Returns playerchar
        """
        global playerchar
        global session
        player_input = Message(dispatcher.get_last_message())
        playerchar = eval("{}()".format(player_input.get_content()))
        session = player_input.get_chat_id()
        player_stats = DialogMessage('stats').get_message() + "\n" \
                       + playerchar.get_stats() + "\n" \
                       + "======================================\n" \
                       + playerchar.get_exp_lvl()
        dispatcher.send_message(player_stats, session)
        Game.adventure(playerchar)

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
                dispatcher.send_message(battle_log, session)
                break
            battle_log += defender.attack(attacker)
            if not attacker.is_alive():
                battle_log += DialogMessage('won_C', defender).get_message()
                dispatcher.send_message(battle_log, session)
                break

    @staticmethod
    def item_drop(enemy):

        if random.randint(1, 6) % 3 == 0:
            item = 'Healing Potion'
            item_healing = random.randint(10, 30)
            dispatcher.send_message(f"You found a {item}!\n" + DialogMessage('healed_CA', playerchar, item_healing).get_message(), session)
            playerchar.set_hp(round(playerchar.get_hp() + item_healing))

        enemy_score = enemy.get_maxhp() + enemy.get_attack()

        def rare_drop(chance):
            if random.random() < chance:
                return RareItem(playerchar.get_lvl())

        def common_drop(chance):
            if random.random() < chance:
                return CommonItem(playerchar.get_lvl())

        def check_drop(item_list):
            for item in item_droplist:
                if item:
                    dispatcher.send_message(DialogMessage('found_item_I', item).get_message() + "\n" + item.get_stats(), session)

                    if playerchar.get_inventory()[item.get_type()]:
                        playeritem = playerchar.get_inventory()[item.get_type()]
                        dispatcher.send_message(f"Comparing to your {playeritem.get_name()}:\n" + item.get_compare_stats(playeritem),
                                                session)

                    dispatcher.send_message("Would you like to equip item? (Y/N)", session)
                    player_input = Message(dispatcher.get_last_message()).get_content()
                    if player_input == 'Y':
                        playerchar.add_item(item)

        if enemy_score > 200:
            item_droplist = [rare_drop(0.6), common_drop(0.2)]
            check_drop(item_droplist)

        if enemy_score > 100:
            item_droplist = [rare_drop(0.6), common_drop(0.2)]
            check_drop(item_droplist)

        if enemy_score > 50:
            item_droplist = [rare_drop(0.2), common_drop(0.3)]
            check_drop(item_droplist)
        else:
            item_droplist = [common_drop(0.3)]
            check_drop(item_droplist)

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
            dispatcher.send_message(DialogMessage('dead').get_message(), session)
            dispatcher.send_message(DialogMessage('end_game').get_message(), session)
        else:
            Game.item_drop(enemy)
            dispatcher.send_message(playerchar.add_exp(enemy.get_maxhp()), session)
            player_stats = DialogMessage('stats').get_message() + "\n" + playerchar.get_stats() + "\n" + playerchar.get_exp_lvl()
            dispatcher.send_message(player_stats, session)

    @staticmethod
    def adventure(playerchar):
        """
        Starts adventure part of game with character 'playerchar'
        Breaks on death or N input
        """
        while playerchar.is_alive():
            dispatcher.send_message(DialogMessage('find_enemy').get_message(), session)
            player_input = Message(dispatcher.get_last_message()).get_content()
            if player_input == 'I':
                dispatcher.send_message(playerchar.get_all_items(), session)
                Game.adventure(playerchar)
                break
            elif player_input == 'N':
                dispatcher.send_message(DialogMessage('end_game').get_message(), session)
                break
            else:
                if random.random() < 0.6:
                    if random.random() < 0.3 and playerchar.get_lvl() >= 4:
                        enemy = GreaterMonster(playerchar.get_lvl())
                    else:
                        enemy = Monster(playerchar.get_lvl())
                    enemy_prompt = DialogMessage('see_enemy_C', enemy).get_message() + "\n" \
                                   + enemy.get_stats() + "\n"
                    dispatcher.send_message(enemy_prompt, session)
                    dispatcher.send_message(DialogMessage('attack_enemy').get_message(), session)
                    player_input = Message(dispatcher.get_last_message()).get_content()
                    if player_input == 'Y':
                        Game.battle_encounter(playerchar, enemy, True)
                    else:
                        Game.adventure(playerchar)
                        break

                else:
                    enemy = Monster(playerchar.get_lvl())
                    enemy_prompt = DialogMessage('enemy_attack_C', enemy).get_message() + "\n" \
                                   + enemy.get_stats() + "\n"
                    dispatcher.send_message(enemy_prompt, session)
                    Game.battle_encounter(playerchar, enemy, False)


# TODO mp -> mf for skills
# TODO skills: Mage Fireball
# TODO skills: Rogue Confusion
# TODO enemies: Dark Shadow
# TODO game: save state
# TODO game: console choice?

def main():
    global dispatcher
    dispatcher = BotHandler(TOKEN)
    while True:
        msg = Message(dispatcher.get_last_message())
        if msg.get_type() != 'text':
            time.sleep(0.5)
            pass
        else:
            if msg.get_content() == '/start':
                dispatcher.send_message('Ready Player One', msg.get_chat_id())
                time.sleep(1)
                dispatcher.send_message(DialogMessage('start_game').get_message(), msg.get_chat_id())
                Game.game_start()
            else:
                time.sleep(0.5)
                pass

if __name__ == '__main__':
    main()
