from events import DialogMessage, StatusMessage
from item import *
from skills import *
import random
import math


class Character:
    _maxhp = 100
    _mp = 0
    _attack = 10
    _exp = 0
    _lvl = 1
    _gold = 0
    _armour = 0
    _character = True
    _hp_item_bonus = 0
    _mp_item_bonus = 0
    _attack_item_bonus = 0
    _armour_item_bonus = 0

    def __init__(self):
        self._cls = 'Character'
        self._inventory = {'Armour': None, 'Weapon': None, 'Helm': None, 'Boots': None, 'Ring': None}
        self._attack_skills = []
        self._defence_skills = []
        self._passives = {}
        self._hp = self._maxhp = self.get_maxhp()

#   Class getters and setters #

    def get_class(self):
        """
        Returns character's class
        """
        return self._cls

    def set_class(self, cls):
        """
        Takes new value for character's class and sets it
        """
        self._cls = cls

    def get_character(self):
        """
        Check if it is a character
        """
        return self._character

#   HP getters and setters #

    def get_current_hp(self):
        """
        Returns character's hp
        """
        return self._hp

    def get_maxhp(self):
        """
        Returns character's maxhp
        """
        return self._maxhp + self.get_hp_modifier()

    def set_hp(self, hp):
        """
        Takes new value for character's hp and sets it
        """
        if 0 < hp <= self.get_maxhp():
            self._hp = hp
        elif hp < 0:
            self._hp = 1
        else:
            self._hp = self.get_maxhp()

    def get_hp_modifier(self):
        """
        Returns character's hp modifier
        """
        return self._hp_item_bonus

    def set_hp_item_bonus(self, hp_bonus):
        """
        Sets character's hp modifier
        """
        self._hp_item_bonus = hp_bonus
        # if character have max hp and unequips item with bonus hp,
        # current hp is recalculated
        if self.get_current_hp() > self.get_maxhp():
            self.set_hp(self.get_maxhp())

#   MP getters and setters #

    def get_mp(self):
        """
        Returns character's mp
        """
        return self._mp + self._mp_item_bonus

    def set_mp(self, mp):
        """
        Takes new value for character's mp and sets it
        """
        self._mp = mp

#   Gold getters and setters #

    def get_gold(self):
        """
        Returns character's mp
        """
        return self._gold

    def set_gold(self, gold):
        """
        Takes new value for character's mp and sets it
        """
        self._gold = gold

#   Attack getters and setters #

    def get_attack_stat(self):
        """
        Returns character's attack stat
        """
        return self._attack + self._attack_item_bonus

    def get_attack(self):
        """
        Returns character's attack (+-10%)
        """
        return random.uniform((self._attack + self._attack_item_bonus) * 0.9, (self._attack + self._attack_item_bonus) * 1.1)

    def set_attack(self, attack):
        """
        Takes new value for character's attack and sets it
        """
        self._attack = attack

    def get_attack_modifier(self):
        """
        Returns character's attack modifier
        Default modifier is 1 and used for player classes
        """
        return 1

#   Defence getters and setters #

    def get_armour(self):
        """
        Returns character's armour
        """
        return self._armour + self._armour_item_bonus

    def set_armour(self, armour):
        """
        Takes new value for character's armour and sets it
        """
        self._armour = armour

    def get_defence_modifier(self):
        """
        Returns character's defence modifier
        """
        return 1 / math.sqrt(self.get_armour()/30 + 1)

#   EXP getters and setters #

    def get_exp(self):
        """
        Returns character's exp
        """
        return self._exp

    def _set_exp(self, exp):
        """
        Takes new value for character's exp and sets it
        Not really intended to use
        Not until I fix problems with lvlup
        """
        self._exp = exp

    def get_exp_to_next_lvl(self):
        """
        Returns character's exp to the next lvl
        """
        return 100 * math.sqrt(self._lvl * 2)

#   LVL getters and setters #

    def get_lvl(self):
        """
        Returns character's lvl
        """
        return self._lvl

    def set_lvl(self, lvl):
        """
        Sets character's lvl
        """
        self._lvl = lvl

#   Adding EXP and lvlup #

    def add_exp(self, exp):
        """
        Adds an amount of exp to character
        """
        self._exp += exp
        if self._exp >= self.get_exp_to_next_lvl():
            self._lvl += 1
            lvlup = DialogMessage('lvlup_CA', {'char': self.get_class(), 'amount': self.get_lvl()}).get_message()
            self.lvlup()
            lvlup += StatusMessage(self).stats_message()
            return lvlup

    def lvlup(self):
        """
        Gives character a lvlup bonus
        """
        self._maxhp += 10
        self._hp = self.get_maxhp()
        self._mp += 1
        self._attack += 1
        self._exp = 0

#   Items and inventory #

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            self._inventory[item.get_type()] = item
            self.recalculate_item_bonus()

    def get_inventory(self):
        """
        Returns character's inventory
        """
        return self._inventory

    def recalculate_item_bonus(self):
        """
        Recalculates all item bonuses
        """
        hp_percent = self.get_current_hp()/self.get_maxhp()
        self._hp_item_bonus = 0
        self._mp_item_bonus = 0
        self._attack_item_bonus = 0
        self._armour_item_bonus = 0
        for i in range(0, len(self._inventory)):
            slot = list(self._inventory)[i]
            item = self._inventory[slot]
            if item is not None:
                self.set_hp_item_bonus(self.get_hp_modifier() + item.get_bonus_hp())
                self._mp_item_bonus += item.get_bonus_mp()
                self._attack_item_bonus += item.get_bonus_attack()
                self._armour_item_bonus += item.get_bonus_defence()
        self.set_hp(self.get_maxhp() * hp_percent)

#   Skills #

    def get_attack_skills(self):
        """
        Returns character's attack skills
        """
        return self._attack_skills

    def get_defence_skills(self):
        """
        Returns character's defence skills
        """
        return self._defence_skills

    def add_attack_skill(self, skill):
        """
        Adds attack skill to character
        """
        self._attack_skills.append(skill)

    def add_defence_skill(self, skill):
        """
        Adds defence skill to character
        """
        self._defence_skills.append(skill)

    def check_defence_skills(self, damage, attacker):
        """
        Checks if any of defence skills are ready to use and uses the first one
        """
        log = ''
        for skill in self.get_defence_skills():
            if skill.is_available():
                skill.update_skill(self)
                log += skill.use_skill(damage, attacker)
                damage = skill.get_leftoverdamage()
                # skill.reset()
                if damage == 0:
                    break
            else:
                skill.set_current_cd(skill.get_current_cd() - 1)
        return damage, log

    def update_skills(self):
        """
        Updates each attack skill with current character's stats
        """
        for skill in self.get_attack_skills() + self.get_defence_skills():
            skill.update_skill(self)

    # def update_defence_skills(self):
    #     """
    #     Updates each defence skill with current character's stats
    #     """
    #     for skill in self.get_defence_skills():
    #         skill.update_skill(self)

    def reset_skills(self):
        """
        Resets each defence skill to default state
        """
        for skill in self.get_defence_skills():
            skill.reset()
        # for skill in self.get_attack_skills():
        #     skill.reset()

    def get_passives(self):
        """
        Returns character's passives (only names and descriptions)
        """
        return self._passives

#   is_alive check #

    def is_alive(self):
        """
        Returns True if character is alive and False if not
        """
        return self._hp > 0

#   Attacking and taking damage #

# Damage types: ['Normal', 'Magic', 'Pure']
# Normal - resisted by armor, does not go through defence skills
# Magic - not resisted by armor, does not go through defence skills
# Pure - not resisted by armor, goes through defence skills

    def take_damage_magic(self, damage, attacker):
        """
        Takes magic damage
        """
        leftoverdamage, log = self.check_defence_skills(damage, attacker)
        if leftoverdamage > 0:
            self._hp -= leftoverdamage
            log += DialogMessage('attack_magic_CAT', {'char': attacker, 'amount': leftoverdamage,
                                                      'target': self.get_class()}).get_message() + "\n"
        return log

    def take_damage_normal(self, damage, attacker):
        """
        Takes normal damage
        """
        leftoverdamage, log = self.check_defence_skills(damage, attacker)
        if leftoverdamage > 0:
            self._hp -= leftoverdamage * self.get_defence_modifier()
            log += DialogMessage('attack_CAT', {'char': attacker, 'amount': leftoverdamage * self.get_defence_modifier(),
                                                'target': self.get_class()}).get_message() + "\n"
        return log

    def take_damage_pure(self, damage, attacker):
        """
        Takes pure damage
        """
        self._hp -= damage
        output = DialogMessage('attack_pure_CAT', {'char': attacker, 'amount': damage,
                                                   'target': self.get_class()}).get_message() + "\n"
        return output

    def attack(self, target):
        """
        Reduces other character's hp by self's attack
        """
        output = None
        log = ''
        for skill in self.get_attack_skills():
            if skill.is_available():
                skill.update_skill(self)
                log += skill.use_skill()
                output = skill.get_damage()
                break
            else:
                skill.set_current_cd(skill.get_current_cd() - 1)
        if output is None:
            attack = self.get_attack() * self.get_attack_modifier()
            output = {'Damage': attack, 'Type': 'Normal'}
        damage_types = {'Normal': target.take_damage_normal,
                        'Magic': target.take_damage_magic,
                        'Pure': target.take_damage_pure}
        log += damage_types[output['Type']](output['Damage'], self.get_class())
        return log

#   Getting character's stats #

    def get_stats(self):
        """
        Returns character's stats in a dictionary
        """
        stats = dict(CLS=self.get_class(),
                     HP=self.get_current_hp(),
                     MAX_HP=self.get_maxhp(),
                     MP=self.get_mp(),
                     ATT=self.get_attack_stat(),
                     ATT_BONUS=self._attack_item_bonus,
                     DEF=1 - self.get_defence_modifier(),
                     LVL=self.get_lvl(),
                     EXP=self.get_exp(),
                     EXPLVL=self.get_exp_to_next_lvl(),
                     GOLD=self.get_gold(),
                     INV=self.get_inventory(),
                     # ATT_SKL=self.get_attack_skills(),
                     # DEF_SKL=self.get_defence_skills(),
                     PASSIVES=self.get_passives())
        return stats

#   testing used stuff #

    def _print_stats(self):
        """
        Prints character's stats
        """
        print(self.get_stats())

    def _get_all_items(self):
        """
        Prints character's inventory
        """
        itemlist = "Slot | Equipped Item\n" \
                   "=========================\n"

        have_items = False
        for item in self.get_inventory():
            if self.get_inventory()[item] is not None:
                itemlist += f"{item} | {self.get_inventory()[item].get_full_name()}\n"
                have_items = True
        # while have_items:
        #     print("Show item stats? (N/Slot)")
        #     slot = input()
        #     if slot in list(self._inventory):
        #         item = self._inventory[slot]
        #         item._print_stats()
        #     else:
        #         break
        if not have_items:
            itemlist += "Your inventory is empty."
        return itemlist


class Mage(Character):
    _maxhp = 90
    _mp = 10
    _attack = 8

    def __init__(self):
        super().__init__()
        self._cls = 'Mage'
        self.add_attack_skill(Fireball(self))
        self.add_defence_skill(EnergyShield(self))
        self._passives['Energy Shield'] = "This passive allows Mage to absorb some of incoming damage.\n" \
                                          "ES scales with MP and lvl"

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            if item.get_type() == 'Weapon':
                item.set_name('Staff')
            super().add_item(item)

    # def get_stats(self):
    #     """
    #     Prints character's stats
    #     """
    #     stats = super().get_stats()
    #     stats['ES'] = self.get_defence_skills()[0].get_es()
    #     return stats


class Warrior(Character):
    hp_mult = 1.1

    def __init__(self):
        super().__init__()
        self._cls = 'Warrior'
        self._hp = self.get_maxhp()
        self._passives['Warrior Blood'] = "This passive adds Warrior additional defence for every missing HP.\n"
        self._passives['Great Health'] = "This passive adds additional defence for Warrior.\n"

#   HP modifier, but with passive #

    def get_hp_modifier(self):
        """
        Returns character's attack modifier
        """
        return self._hp_item_bonus

    def get_maxhp(self):
        """
        Returns character's maxhp
        """
        return (self._maxhp + self.get_hp_modifier()) * self.hp_mult

#   Class specific methods modifications #

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            if item.get_type() == 'Weapon':
                item.set_name('Sword')
            super().add_item(item)

    # def get_stats(self):
    #     """
    #     Returns character's stats in a dictionary
    #     """
    #     stats = super().get_stats()
    #     stats['DEF_BONUS'] = self.get_passive_defence_bonus()
    #     stats['HP_BONUS'] = self.hp_mult
    #     return stats


class Rogue(Character):
    _attack = 12
    _maxhp = 90

    def __init__(self):
        super().__init__()
        self._cls = 'Rogue'
        self.add_attack_skill(CriticalStrike(self))
        self.add_defence_skill(Evasion(self))
        self._passives['Evasion'] = "This passive allows Rogue to evade some of incoming damage.\n" \
                                    "EV scales with MP"
        self._passives['Critical Strike'] = "This passive allows Rogue to double the damage some of his attacks.\n" \
                                            "Crit chance scales with MP"

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            if item.get_type() == 'Weapon':
                item.set_name('Dagger')
            super().add_item(item)

    # def get_stats(self):
    #     """
    #     Returns character's stats in a dictionary
    #     """
    #     stats = super().get_stats()
    #     stats['EV_CHANCE'] = self.get_evasion()
    #     stats['CRIT_CHANCE'] = self.get_crit_chance()
    #     return stats


class Monster(Character):
    def __init__(self, lvl_mult=1):
        super().__init__()
        self._cls = 'Monster'
        self._lvl_mult = lvl_mult * 2 / math.sqrt(lvl_mult * 3)
        self._maxhp = (random.randint(16, 40) * self._lvl_mult)
        self._hp = self.get_maxhp()
        self._mp = (random.randint(1, 1) * self._lvl_mult)
        self._attack = (random.randint(5, 10) * self._lvl_mult)
        self._armour = 5 * random.uniform(1, 2)


class GreaterMonster(Monster):
    def __init__(self, lvl_mult=1):
        lvl_mult *= 1.5
        super().__init__(lvl_mult)
        self._cls = 'Greater Monster'
        self.add_item(RareItem(int(lvl_mult/2)))
        self.add_item(RareItem(int(lvl_mult/2)))
        self.add_item(RareItem(int(lvl_mult/2)))
        self.add_item(RareItem(int(lvl_mult/2)))
        self._hp = self.get_maxhp()
        self._mp = self.get_mp()
        if random.random() > 0.5:
            self.add_attack_skill(VoidStrike(self))
