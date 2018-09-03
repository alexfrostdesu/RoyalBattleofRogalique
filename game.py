from classes import *
from events import PrintMessage
import random


class Game:

    @staticmethod
    def game_start():
        """
        Character selection string
        Returns playerchar
        """
        PrintMessage('start_game')
        global playerchar
        playerchar = eval("{}()".format(input()))
        PrintMessage('stats')
        playerchar.print_stats()
        Game.adventure(playerchar)

    @staticmethod
    def battle_until_death(attacker, defender):
        """
        Takes attacker's and defender's characters and battles them until one of them is dead
        """
        while attacker.is_alive() and defender.is_alive():
            attacker.deal_damage(defender)
            if not defender.is_alive():
                PrintMessage('won_C', attacker)
                break
            defender.deal_damage(attacker)
            if not attacker.is_alive():
                PrintMessage('won_C', defender)
                break

    @staticmethod
    def item_drop(enemy):

        if random.randint(1, 6) % 3 == 0:
            item = 'Healing Potion'
            print(f"You found a {item}!")
            # PrintMessage('found_item_I', item)
            item_healing = random.randint(10, 30)
            PrintMessage('healed_CA', playerchar, item_healing)
            playerchar.set_hp(round(playerchar.get_hp() + item_healing))
        enemy_score = enemy.get_maxhp() + enemy.get_attack()

        def rare_drop(chance):
            if random.random() < chance:
                return RareItem(playerchar.get_lvl())

        def common_drop(chance):
            if random.random() < chance:
                return CommonItem(playerchar.get_lvl())

        if enemy_score > 200:
            playerchar.add_item(rare_drop(0.6))
            playerchar.add_item(common_drop(0.2))

        if enemy_score > 100:
            playerchar.add_item(rare_drop(0.3))
            playerchar.add_item(common_drop(0.6))

        if enemy_score > 50:
            playerchar.add_item(rare_drop(0.2))
            playerchar.add_item(common_drop(0.3))
        else:
            playerchar.add_item(common_drop(0.3))

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
            PrintMessage('dead')
            PrintMessage('end_game')
        else:
            Game.item_drop(enemy)
            playerchar.add_exp(enemy.get_maxhp())
            PrintMessage('stats')
            playerchar.print_stats()
            playerchar.print_exp_lvl()

    @staticmethod
    def adventure(playerchar):
        """
        Starts adventure part of game with character 'playerchar'
        Breaks on death or N input
        """
        while playerchar.is_alive():
            PrintMessage('find_enemy')
            player_input = input()
            if player_input == 'I':
                playerchar.print_inventory()
                Game.adventure(playerchar)
                break
            elif player_input == 'N':
                PrintMessage('end_game')
                break
            else:
                if random.random() < 0.6:
                    if random.random() < 0.3 and playerchar.get_lvl() >= 4:
                        enemy = GreaterMonster(playerchar.get_lvl())
                    else:
                        enemy = Monster(playerchar.get_lvl())
                    PrintMessage('see_enemy_C', enemy)
                    enemy.print_stats()
                    PrintMessage('attack_enemy')
                    if input() == 'Y':
                        Game.battle_encounter(playerchar, enemy, True)
                    else:
                        Game.adventure(playerchar)
                        break

                else:
                    enemy = Monster(playerchar.get_lvl())
                    PrintMessage('enemy_attack_C', enemy)
                    enemy.print_stats()
                    Game.battle_encounter(playerchar, enemy, False)


# TODO mp -> mf for skills
# TODO skills: Mage Fireball
# TODO skills: Rogue Confusion
# TODO enemies: Dark Shadow
# TODO game: save state
# TODO game: console choice?


if __name__ == '__main__':
    Game.game_start()
    global playerchar

