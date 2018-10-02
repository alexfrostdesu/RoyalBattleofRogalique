from events import DialogMessage
from item import *
import random
import math


class Character:
    default_hp = 100
    default_mp = 0
    default_attack = 10
    default_exp = 0
    default_lvl = 1
    _character = True

    def __init__(self):
        self._cls = 'Character'
        self._armour = 0
        self._stash = []
        self._inventory = {'Armor': None, 'Weapon': None, 'Helm': None, 'Boots': None, 'Ring': None}
        self._maxhp = self._hp = self.default_hp
        self._maxmp = self._mp = self.default_mp
        self._skills = []
        self._attack = self.default_attack
        self._lvl = self.default_lvl
        # self._exp_to_next_lvl = self.default_exp_to_next_lvl
        self._exp = self.default_exp
        self.recount_item_bonus()

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
        if hp <= self.get_maxhp():
            self._hp = hp
        else:
            self._hp = self.get_maxhp()

    def get_hp_modifier(self):
        """
        Returns character's attack modifier
        """
        return self._hp_item_bonus

#   MP getters and setters #

    def get_current_mp(self):
        """
        Returns character's mp
        """
        return self._mp

    def get_maxmp(self):
        """
        Returns character's hp
        """
        return self._maxmp + self._mp_item_bonus

    def set_mp(self, mp):
        """
        Takes new value for character's mp and sets it
        """
        self._mp = mp

#   Attack getters and setters #

    def get_attack(self):
        """
        Returns character's attack
        """
        return self._attack + self._attack_item_bonus

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
        return 1 - (math.log10(self.get_armour() + 1) / 3)

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
        return 100 * math.sqrt(self._lvl)

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
            return self.lvlup()

    def lvlup(self):
        """
        Gives character a lvlup bonus
        """
        self._maxhp += 10
        self._hp = self.get_maxhp()
        self._maxmp += 1
        self._mp = self.get_maxmp()
        self._attack += 1
        self._exp = 0
        # return DialogMessage('lvlup_C', self).get_message()

#   Items and inventory #

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            self._inventory[item.get_type()] = item
            self.recount_item_bonus()

    def get_inventory(self):
        """
        Returns character's inventory
        """
        return self._inventory

    def recount_item_bonus(self):
        """
        Recounts all item bonuses
        """
        self._hp_item_bonus = 0
        self._mp_item_bonus = 0
        self._attack_item_bonus = 0
        self._armour_item_bonus = 0
        for i in range(0, len(self._inventory)):
            slot = list(self._inventory)[i]
            item = self._inventory[slot]
            if item is not None:
                self._hp_item_bonus += item.get_bonus_hp()
                self._mp_item_bonus += item.get_bonus_mp()
                self._attack_item_bonus += item.get_bonus_attack()
                self._armour_item_bonus += item.get_bonus_defence()

#   Skills #

    def get_skills(self):
        """
        Returns character's skills
        """
        return self._skills


    def add_skill(self, skill):
        """
        Adds skill to character
        """
        self._skills += skill

        # skill = {'TYPE': True (Attack) or False (Defence), 'NAME' = 'SkillName', 'POWER' = amount, 'CD' = amount, 'CD_MAX' = amount}

#   is_alive check #

    def is_alive(self):
        """
        Returns True if character is alive and False if not
        """
        return self._hp > 0

#   Attacking and taking damage #

    def take_damage_from(self, damage, other):
        """
        Takes damage from other character
        Prints message about that attack
        """
        self._hp -= damage * self.get_defence_modifier()
        # return DialogMessage('attack_CAT', other, damage, self).get_message()  + "\n"

    def take_damage_pure(self, damage):
        """
        Takes pure damage
        """
        self._hp -= damage

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        attack = self.get_attack() * self.get_attack_modifier()
        return other.take_damage_from(self, attack)

#   Getting character's stats #

    def get_stats(self):
        """
        Returns character's stats in a dictionary
        """
        stats = dict(CLS=self.get_class(),
                     HP=int(self.get_current_hp()),
                     MAX_HP=int(self.get_maxhp()),
                     MP=int(self.get_current_mp()),
                     MAX_MP=int(self.get_maxmp()),
                     ATT=int(self.get_attack()),
                     DEF=round(self.get_defence_modifier(), 2),
                     EXP=int(self.get_exp()),
                     EXPLVL=int(self.get_exp_to_next_lvl()))
        # stats_msg = f"Class: {self._cls}\n" \
        #             f"HP: {self._hp:1.0f}/{self.get_maxhp():1.0f} || MP: {self._mp:1.0f}/{self.get_maxmp():1.0f}\n" \
        #             f"Attack: {self._attack:1.0f}+{self._attack_modifier} || Defense Bonus: {(self.get_defence_modifier()) * 100:1.0f}%\n"
        return stats

#   legacy used stuff #

    def print_stats(self):
        """
        Prints character's stats
        """
        print(self.get_stats())

    def get_all_items(self):
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
        #         item.print_stats()
        #     else:
        #         break
        if not have_items:
            itemlist += "Your inventory is empty."
        return itemlist

    # def get_exp_lvl(self):
    #     """
    #     Prints character's current level, exp and exp needed for next level
    #     """
    #     return f"Current Level: {self._lvl:1.0f}, Current Experience: {self._exp:1.0f}, Next Level: {self._exp_to_next_lvl:1.0f}"


class Mage(Character):
    default_hp = 85
    default_mp = 10
    default_attack = 8

    def __init__(self):
        super().__init__()
        self.add_skill({'TYPE': True, 'NAME': 'Fireball', 'POWER': self.get_current_mp() * 3, 'CD': 3, 'CD_MAX': 3})
        self._es = self.get_es()

#   ES getter and setter #

    def get_es(self):
        """
        Returns character's es
        """
        return self.default_mp * (self.get_lvl() / 2)

    def _set_es(self, es):
        """
        Takes new value for character's es and sets it
        Not really intended to use
        """
        self._es = es

#   Class specific methods modifications #

    def lvlup(self):
        """
        Gives character a lvlup bonus
        """
        super().lvlup()
        self._es = self.get_es()

    def take_damage_from(self, damage, other):
        """
        Takes other character's attack and reduces self es or/and hp by it
        Prints message about that attack
        """
        if self._es > 0 and damage < self._es:
            self._es -= damage
            # return DialogMessage('attack_es_CAT', other, damage, self).get_message() + "\n"
        elif 0 < self._es <= damage:
            if self._es == damage:
                broke_es = True
                self._es = 0
                # return DialogMessage('broke_es_C', self).get_message() + "\n"
            else:
                leftoverdmg = damage - self._es
                broke_es = True
                self._hp -= leftoverdmg * self.get_attack_modifier()
                self._es = 0
                # return DialogMessage('broke_es_dmg_hp_CAT', other, damage, self).get_message() + "\n"
        else:
            return super().take_damage_from(damage, other)

    def get_stats(self):
        """
        Prints character's stats
        """
        stats = super().get_stats()
        stats['ES'] = self._es
        return stats


class Warrior(Character):
    default_hp = 110
    hp_mult = 1.1

    def __init__(self):
        super().__init__()
        self._cls = 'Warrior'
        self._maxhp = self._hp = self.default_hp * self.hp_mult

#   HP modifier, but with passive #

    def get_hp_modifier(self):
        """
        Returns character's attack modifier
        """
        return self._hp_item_bonus * self.hp_mult

#   Armour passive getter #

    def get_passive_defence_bonus(self):
        """
        Returns warrior's passive defence bonus
        """
        return 1 - (math.log10(self.get_maxhp() - self.get_current_hp() + 1) / 10)

#   Class specific methods modifications #

    def get_defence_modifier(self):
        """
        Returns character's defence modifier
        """
        return 1 - (math.log10(self.get_armour() + 1) / 3) - self.get_passive_defence_bonus()

    def get_stats(self):
        """
        Returns character's stats in a dictionary
        """
        stats = super().get_stats()
        stats['DEF_BONUS'] = self.get_passive_defence_bonus()
        stats['HP_BONUS'] = self.hp_mult
        return stats


class Rogue(Character):
    crit_chance = 0.2
    evade_chance = 0.2
    default_attack = 15

    def __init__(self):
        super().__init__()

#   Evasion getters and setters #

    def get_evasion(self):
        """
        Returns character's evade chance
        """
        return self.evade_chance

    def set_evasion(self, ev):
        """
        Sets character's evade chance
        """
        self.evade_chance = ev

    def get_dodge(self):
        """
        Returns evasion proc True or False
        """
        return random.random() < self.get_evasion()

#   Crit getters and setters #

    def get_crit_chance(self):
        """
        Returns character's evade chance
        """
        return self.crit_chance

    def set_crit_chance(self, chance):
        """
        Takes new value for character's evade chance and sets it
        """
        self.crit_chance = chance

    def get_crit(self):
        """
        Returns crit proc True or False
        """
        return random.random() < self.get_crit_chance()

#   Class specific methods modifications #

    def take_damage_from(self, damage, other):
        """
        Takes damage from other character
        Prints message about that attack
        """
        if not self.get_dodge():
            return super().take_damage_from(damage, other)
        else:
            pass
            # DialogMessage('evaded_CA', self, damage).get_message()  + "\n"

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        if self.get_crit():
            attack = self.get_attack() * self.get_attack_modifier() * 2
            # DialogMessage('crit', self, damage).get_message()  + "\n"
        else:
            attack = self.get_attack() * self.get_attack_modifier()
        return other.take_damage_from(attack, self)

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

    def get_stats(self):
        """
        Returns character's stats in a dictionary
        """
        stats = super().get_stats()
        stats['EV_CHANCE'] = self.get_evasion()
        stats['CRT_CHANCE'] = self.get_crit_chance()
        return stats


class Monster(Character):
    def __init__(self, lvl_mult=1):
        super().__init__()
        self._lvl_mult = lvl_mult / math.sqrt(lvl_mult)
        self._maxhp = self._hp = (random.randint(20, 40) * self._lvl_mult)
        self._mp = self._maxmp = (random.randint(1, 1) * self._lvl_mult)
        self._attack = (random.randint(1, 15) * self._lvl_mult)

    def add_item(self, item):
        if item is None:
            pass
        else:
            self._inventory[item.get_type()] = item
            self.recount_item_bonus()


class GreaterMonster(Monster):
    def __init__(self, lvl_mult=1):
        lvl_mult *= 2 * math.log10(lvl_mult)
        super().__init__(lvl_mult)
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self._hp = self.get_maxhp()
        self._mp = self.get_maxmp()


# TESTING #

testwar = Monster()
testwar.print_stats()
testwar.add_exp(100)
testwar.print_stats()
testwar.add_exp(100)
testwar.print_stats()
testwar.add_exp(100)
testwar.print_stats()
testwar.take_damage_from(20, None)
testwar.print_stats()
testwar.take_damage_from(20, None)
testwar.print_stats()
testwar.take_damage_from(20, None)
testwar.print_stats()
testwar.take_damage_from(20, None)
testwar.add_exp(100)
testwar.add_exp(100)
testwar.print_stats()
