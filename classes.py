from events import DialogMessage
from item import *
import random
import math


class Character:
    default_hp = 100
    default_mp = 10
    default_attack = 10
    default_exp = 0
    default_lvl = 1
    default_exp_to_next_lvl = 100 + default_lvl * 10

    def __init__(self):
        self._cls = self.__class__.__name__
        self._defense = 1
        self._stash = []
        self._inventory = {'Armor': None, 'Weapon': None, 'Helm': None, 'Boots': None, 'Ring': None}
        self._maxhp = self._hp = self.default_hp
        self._maxmp = self._mp = self.default_mp
        self._attack = self.default_attack
        self._lvl = self.default_lvl
        self._exp_to_next_lvl = self.default_exp_to_next_lvl
        self._exp = self.default_exp
        self.recount_bonus()

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

    def get_hp(self):
        """
        Returns character's hp
        """
        return self._hp

    def get_maxhp(self):
        """
        Returns character's maxhp
        """
        return self._maxhp + self._hp_modifier

    def set_hp(self, hp):
        """
        Takes new value for character's hp and sets it
        """
        if hp <= self.get_maxhp():
            self._hp = hp
        else:
            self._hp = self.get_maxhp()

    def get_mp(self):
        """
        Returns character's mp
        """
        return self._mp

    def get_maxmp(self):
        """
        Returns character's hp
        """
        return self._maxmp + self._mp_modifier

    def set_mp(self, mp):
        """
        Takes new value for character's mp and sets it
        """
        self._mp = mp

    def get_attack(self):
        """
        Returns character's attack
        """
        return self._attack + self._attack_modifier

    def set_attack(self, attack):
        """
        Takes new value for character's attack and sets it
        """
        self._attack = attack

    def get_defense(self):
        """
        Returns character's defense bonus
        """
        return self._defense + self._defense_modifier

    def set_defence(self, defense):
        """
        Takes new value for character's attack and sets it
        """
        self._defense = defense

    def get_exp(self):
        """
        Returns character's exp
        """
        return self._exp

    def get_exp_to_next_lvl(self):
        """
        Returns character's exp to the next lvl
        """
        return self._exp_to_next_lvl

    def _set_exp(self, exp):
        """
        Takes new value for character's exp and sets it
        """
        self._exp = exp

    def get_exp_lvl(self):
        """
        Prints character's current level, exp and exp needed for next level
        """
        return f"Current Level: {self._lvl:1.0f}, Current Experience: {self._exp:1.0f}, Next Level: {self._exp_to_next_lvl:1.0f}"

    def add_exp(self, exp):
        """
        Adds a amount of exp to character
        """
        self._exp += exp
        if self._exp > self._exp_to_next_lvl:
            self._lvl += 1
            self._exp_to_next_lvl = 100 * math.sqrt(self._lvl)
            return self.lvlup()

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        if item is None:
            pass
        else:
            self._inventory[item.get_type()] = item
            self.recount_bonus()

    def get_inventory(self):
        """
        Returns character's inventory
        """
        return self._inventory

    def recount_bonus(self):
        """
        Recounts all item bonuses
        """
        self._hp_modifier = 0
        self._mp_modifier = 0
        self._attack_modifier = 0
        self._defense_modifier = 0
        for i in range(0, len(self._inventory)):
            slot = list(self._inventory)[i]
            item = self._inventory[slot]
            if item is not None:
                self._hp_modifier += item.get_bonus_hp()
                self._mp_modifier += item.get_bonus_mp()
                self._attack_modifier += item.get_bonus_attack()
                self._defense_modifier += item.get_bonus_defence()

    def get_lvl(self):
        """
        Returns character's exp
        """
        return self._lvl

    def is_alive(self):
        """
        Returns True if character is alive and False if not
        """
        return self._hp > 0

    def lvlup(self):
        """
        Gives character a lvlup bonus
        """
        self._maxhp += 10
        self._hp = self.get_maxhp()
        self._maxmp += 10
        self._mp = self.get_maxmp()
        self._attack += 1
        self._exp = 0
        return DialogMessage('lvlup_C', self).get_message()

    def get_defence_modifier(self):
        """
        Returns character's defence modifier
        """
        if self.get_defense() > 2:
            return math.log10(math.sqrt(self.get_defense() / 2))
        else:
            return self.get_defense() / 20

    def take_damage(self, other, damage):
        """
        Takes other character's attack and reduces self hp by it
        Prints message about that attack
        """
        self._hp -= damage
        return DialogMessage('attack_CAT', other, damage, self).get_message()  + "\n"

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        reduction = 1 - other.get_defence_modifier()
        return other.take_damage(self, self.get_attack() * reduction)

    def get_stats(self):
        """
        Returns character's stats
        """
        stats_msg = f"Class: {self._cls}\n" \
                    f"HP: {self._hp:1.0f}/{self.get_maxhp():1.0f} || MP: {self._mp:1.0f}/{self.get_maxmp():1.0f}\n" \
                    f"Attack: {self._attack:1.0f}+{self._attack_modifier} || Defense Bonus: {(self.get_defence_modifier()) * 100:1.0f}%\n"
        return stats_msg

    def print_stats(self):
        """
        Prints character's stats
        """
        stats_msg = self.get_stats()
        print(stats_msg)

    def get_all_items(self):
        """
        Prints character's inventory
        """
        itemlist = "Slot | Equipped Item\n" \
                   "=========================\n"

        have_items = False
        for item in self.get_inventory():
            if self.get_inventory()[item] is not None:
                itemlist += f"{item} | {self.get_inventory()[item].get_name()}\n"
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


class Mage(Character):
    def __init__(self, es_mult=0.3):
        super().__init__()
        self._es_mult = es_mult
        self._es = self._max_es = self._hp * self._es_mult

    def get_es(self):
        """
        Returns character's es
        """
        return self._es

    def lvlup(self):
        """
        Gives character a lvlup bonus
        """
        self._es = self._max_es
        return super().lvlup()

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        super().add_item(item)
        if self.get_inventory()['Weapon'] is not None:
            self.get_inventory()['Weapon'].set_type('Wand')

    def take_damage(self, other, damage):
        """
        Takes other character's attack and reduces self es or/and hp by it
        Prints message about that attack
        """
        if self._es > 0 and damage < self._es:
            self._es -= damage
            return DialogMessage('attack_es_CAT', other, damage, self).get_message() + "\n"
        elif 0 < self._es <= damage:
            if self._es == damage:
                broke_es = True
                self._es = 0
                return DialogMessage('broke_es_C', self).get_message() + "\n"
            else:
                leftoverdmg = damage - self._es
                broke_es = True
                self._hp -= leftoverdmg
                self._es = 0
                return DialogMessage('broke_es_dmg_hp_CAT', other, damage, self).get_message() + "\n"
        else:
            return super().take_damage(other, damage)

    def get_stats(self):
        """
        Prints character's stats
        """
        stats_msg = super().get_stats() + f"Special: Energy Shield {self._es:1.0f}"
        return stats_msg


class Warrior(Character):
    def __init__(self, hp_mult=1.2):
        super().__init__()
        self._hp_mult = hp_mult
        self._hp *= self._hp_mult
        self._maxhp = self._hp

    def get_defense(self):
        """
        Returns character's defense bonus
        """
        blood_defense_bonus = math.sqrt(self.get_maxhp() - self._hp) / 1.4
        return self._defense + self._defense_modifier + blood_defense_bonus

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        super().add_item(item)
        if self.get_inventory()['Weapon'] is not None:
            self.get_inventory()['Weapon'].set_type('Sword')

    def get_stats(self):
        """
        Prints character's stats
        """
        stats_msg = super().get_stats() + "Special: Blood Defense"
        return stats_msg

class Rogue(Character):
    def __init__(self, crit_chance=0.2, evade_chance=0.2):
        super().__init__()
        self._evade_chance = evade_chance
        self._crit_chance = crit_chance

    def get_dodge(self):
        """
        Returns character's evade chance
        """
        return self._evade_chance

    def set_dodge(self, dodge):
        """
        Takes new value for character's evade chance and sets it
        """
        self._evade_chance = dodge

    def get_crit_chance(self):
        """
        Returns character's evade chance
        """
        return self._crit_chance

    def set_crit_chance(self, chance):
        """
        Takes new value for character's evade chance and sets it
        """
        self._crit_chance = chance

    def take_damage(self, other, damage):
        """
        Takes other character's attack and reduces self hp by it or dodges the attack
        Prints message about that attack
        """
        if random.random() >= self._evade_chance:
            return super().take_damage(other, damage)
        else:
            return DialogMessage('evaded_CA', self, damage).get_message()  + "\n"

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        reduction = 1 - other.get_defence_modifier()
        if random.random() < self.get_crit_chance():
            return DialogMessage('crit').get_message() + "\n"\
                   + other.take_damage(self, self.get_attack() * 2 * reduction)
        else:
            return other.take_damage(self, self.get_attack() * reduction)

    def add_item(self, item):
        """
        Adds an item to character inventory
        """
        super().add_item(item)
        if self.get_inventory()['Weapon'] is not None:
            self.get_inventory()['Weapon'].set_type('Knife')

    def get_stats(self):
        """
        Prints character's stats   wfafsfa
        """
        stats_msg = super().get_stats() + f"Special: Evasion Chance {self._evade_chance * 100:1.0f}%"
        return stats_msg



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
            self.recount_bonus()


class GreaterMonster(Monster):
    def __init__(self, lvl_mult=1):
        lvl_mult *= 2 * math.log10(lvl_mult)
        super().__init__(lvl_mult)
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self._hp = self.get_maxhp()
        self._mp = self.get_maxmp()