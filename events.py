class DialogMessage:
    def __init__(self, code, object=None, amount=-1, target=None):
        self._character = ''
        self._item = ''
        self._amount = 0
        self._target = ''
        if object is not None and (object.get_character() or object.__class__.__bases__[0].__name__ in ('Character', 'Monster')):
            self._character = object.get_class()
        elif object.__class__.__name__ == 'Item' or object.__class__.__bases__[0].__name__ == 'Item':
            self._item = object.get_full_name()
        if amount >= 0:
            self._amount = str(round(amount, 1))
        if target is not None and (target.get_character() or target.__class__.__bases__[0].__name__ in ('Character', 'Monster')):
            self._target = target.get_class()
        # with open('all_messages.txt') as msg_list:
        #     all_messages = dict(x.rstrip().split(':') for x in msg_list)
        all_messages = dict(attack_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} HP* damage!",
                            attack_es_CAT=f"*{self._character}* attacked *{self._target}* for {self._amount} ES damage!",
                            broke_es_C=f"*{self._character}*'s Energy Shield is destroyed!",
                            broke_es_dmg_hp_CAT=f"*{self._character}* broke *{self._target}*'s Energy Shield, while also dealing *{self._amount}* HP damage!",
                            evaded_CA=f"{self._character} evaded {self._amount} damage!",
                            crit="Critical hit!",
                            lvlup_CA=f"{self._character} got a level up! Your level is now {self._amount}",
                            healed_CA=f"{self._character} was healed for {self._amount} HP",
                            won_C=f"{self._character} has won the battle!",
                            lost_C=f"{self._character} has lost the battle!",
                            stats="Your character's stats",
                            start_game="*Select your character*:```\nMage \nWarrior \nRogue```",
                            base="Do you want to go and kill some monsters? *(Y/I/S)*```\nY - Go and find some monsters \nI - Show inventory \nS - Show stats```",
                            see_enemy_C=f"You see a {self._character} in the distance.",
                            attack_enemy="Do you want to attack? *(Y/N)*```\nY - Attack the enemy \nN - Retreat to base```",
                            enemy_attack_C=f"You are attacked by {self._character}!",
                            found_item_I=f"You found a {self._item}!",
                            end_game="Your adventure ends here.\nType /start to start new game.",
                            dead="Your character is dead.",
                            equip_item="Would you like to equip item? *(Y/N)*```\nY - Equip Item \nN - Discard Item```")
        self._message = all_messages[code]

    def get_message(self):
        return self._message

    def print_message(self):
        print(self._message)


class StatusMessage:
    def __init__(self, character):
        self._character = character
        self._stats = self._character.get_stats()

    def stats_message(self):
        msg = f"*{self._stats['CLS']}'s stats:*\n" \
              f"`HP      |  {self._stats['HP']:1.0f}/{self._stats['MAX_HP']:1.0f}`\n" \
              f"`MP      |  {self._stats['MP']:1.0f}`\n" \
              f"`Attack  |  {self._stats['ATT'] - self._stats['ATT_BONUS']:1.0f} + {self._stats['ATT_BONUS']:1.0f}`\n" \
              f"`Defence |  {self._stats['DEF'] * 100:1.0f}%`\n" \
              f"`LVL     |  {self._stats['LVL']}`\n" \
              f"`EXP     |  {self._stats['EXP']:1.0f}/{self._stats['EXPLVL']:1.0f}`"
        return msg

    def inventory_message(self):
        inventory = self._character.get_inventory()
        msg = f"*Your {self._stats['CLS']}'s inventory:*\n" \
              "`Slot    | Equipped Item`\n" \
              "`=======================`\n"
        for item in [i for i in inventory.keys()]:
            if inventory[item] is not None:
                msg += f"`{item}".ljust(9) + f"| {inventory[item].get_full_name()}`\n"
            else:
                msg += f"`{item}".ljust(9) + "| No Item`\n"
        return msg