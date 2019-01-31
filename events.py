class DialogMessage:
    def __init__(self, code, params={}):
        self._code = code
        self._character = params.get('char')
        self._skill = params.get('skill')
        self._item = params.get('item')
        self._amount = params.get('amount')
        self._target = params.get('target')
        if self._amount is not None:
            self._amount = str(round(self._amount, 1))

    def get_message(self):
        messages = dict(
            stats="Your character's stats",
            start_game="*Select your character*:\n",
            base="Do you want to go and kill some monsters? \n" + "```\nGo and find some monsters \nShow inventory \nShow stats \nGo to shop```",
            attack_enemy="Do you want to attack? \n" + "```\nAttack the enemy \nFlee to the base```",
            attack_boss="Do you want to attack? \n" + "```\nAttack boss \nReturn to the base```",
            end_game="Your adventure ends here.",
            dead="Your character is dead.",
            equip_item="Would you like to equip item? \n" + "```\nEquip Item \nDiscard Item```")
        if self._character != '' or self._item != '':
            action_messages = dict(
                attack_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} HP* damage!",
                attack_magic_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} magic* damage!",
                attack_pure_CAT=f"*{self._target}* received *{self._amount} pure* damage!",
                attack_es_CAT=f"*{self._character}* attacked *{self._target}* for *{self._amount} ES* damage!",
                used_skill_C=f"*{self._character}* used {self._skill}!",
                broke_es_C=f"*{self._character}*'s Energy Shield is destroyed!",
                broke_es_dmg_hp_CAT=f"*{self._character}* broke *{self._target}*'s Energy Shield, while also dealing *{self._amount}* HP damage!",
                evaded_CA=f"*{self._character}* evaded *{self._amount}* damage!",
                crit="Critical hit!",
                lvlup_CA=f"*{self._character}* got a level up! Your level is now {self._amount}\n",
                healed_CA=f"{self._character} was healed for a {self._amount} HP",
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
        for stat in self._stats:
            if stat is float:
                stat = round(stat, 2)

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
        if self._character.get_all_skills():
            msg += f"Skills:\n"
            for skill in self._character.get_all_skills():
                msg += f"`{skill.get_name()}`\n"
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

    def shop_message(self):
        player_hp = self._character.get_current_hp()
        player_max_hp = self._character.get_maxhp()
        msg = "*Welcome to the shop!*\n" \
              f"Current gold: {self._character.get_gold()} \n" \
               "What would you like to buy? *(HP/SP/MP/A/M)*\n" \
               f"`HP refill:     {player_max_hp - player_hp:1.0f} gold`\n" \
                "`Small Potion:  10 gold` \n" \
                "`Medium Potion: 100 gold` \n" \
                "`Attack boost:  500 gold` \n" \
                "`MP boost:      500 gold` \n" \
                "Type *E* to exit shop"
        return msg

    def skills_message(self):
        skills = self._character.get_all_skills()
        msg = "Your character's skills: \n"
        for skill in skills:
            msg += "\n"
            msg += skill.get_stats()
        return msg
