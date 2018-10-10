class DialogMessage:
    def __init__(self, code, object=None, amount=-1, target=None):
        self._code = code
        self._character = ''
        self._skill = ''
        self._item = ''
        self._amount = 0
        self._target = ''
        if object is not None and (
                object.get_character() or object.__class__.__bases__[0].__name__ in ('Character', 'Monster')):
            self._character = object.get_class()
            if object.is_skill_available():
                self._skill = object.first_available_skill().get_name()
        elif object.__class__.__name__ == 'Item' or object.__class__.__bases__[0].__name__ == 'Item':
            self._item = object.get_full_name()
        if amount >= 0:
            self._amount = str(round(amount, 1))
        if target is not None and (
                target.get_character() or target.__class__.__bases__[0].__name__ in ('Character', 'Monster')):
            self._target = target.get_class()

    def get_message(self):
        messages = dict(
            stats="Your character's stats",
            start_game="*Select your character*:\n" + "```\nMage \nWarrior \nRogue```",
            base="Do you want to go and kill some monsters? *(Y/I/S)*\n" + "```\nY - Go and find some monsters \nI - Show inventory \nS - Show stats```",
            attack_enemy="Do you want to attack? *(Y/N)*\n" + "```\nY - Attack the enemy \nN - Retreat to base```",
            end_game="Your adventure ends here.\nType /start to start new game.",
            dead="Your character is dead.",
            equip_item="Would you like to equip item? *(Y/N)*\n" + "```\nY - Equip Item \nN - Discard Item```")
        if self._character != '' or self._item != '':
            action_messages = dict(
                attack_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} HP* damage!",
                attack_pure_CAT=f"That damaged *{self._target}* for *{self._amount} HP*!",
                attack_es_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} ES* damage!",
                used_skill_C=f"*{self._character}* used {self._skill}!",
                broke_es_C=f"*{self._character}*'s Energy Shield is destroyed!",
                broke_es_dmg_hp_CAT=f"*{self._character}* broke *{self._target}*'s Energy Shield, while also dealing *{self._amount}* HP damage!",
                evaded_CA=f"{self._character} evaded {self._amount} damage!",
                crit="Critical hit!",
                lvlup_CA=f"*{self._character}* got a level up! Your level is now {self._amount}\n",
                healed_CA=f"{self._character} was healed for {self._amount} HP",
                won_C=f"{self._character} has won the battle!",
                lost_C=f"{self._character} has lost the battle!",
                dead_C=f"{self._character} is dead.",
                see_enemy_C=f"You see a {self._character} in the distance.",
                enemy_attack_C=f"You are attacked by {self._character}!",
                found_item_I=f"You found a {self._item}!")
        else:
            action_messages = dict()
        messages.update(action_messages)
        self._message = messages[self._code]
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
              f"`EXP     |  {self._stats['EXP']:1.0f}/{self._stats['EXPLVL']:1.0f}`\n" \
              f"`Gold    |  {self._stats['GOLD']:1.0f}`\n"
        if self._stats.get('ES'):
            msg += f"`ES      |  {self._stats['ES']:1.0f}`\n"
        if self._stats.get('EV_CHANCE'):
            msg += f"`EV      |  {self._stats['EV_CHANCE'] * 100:0.1f}%`\n"
        if self._stats.get('CRIT_CHANCE'):
            msg += f"`Crit    |  {self._stats['CRIT_CHANCE'] * 100:0.1f}%`\n"
        if self._stats.get('PASSIVES'):
            msg += f"Passive skills:\n"
            for passive in self._stats['PASSIVES']:
                msg += f"`{passive}`\n"
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
