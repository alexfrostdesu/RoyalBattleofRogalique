from events import DialogMessage, StatusMessage
from item import *
import random
import math


class Character:
    _maxhp = 100
    _mp = 0
    _attack = 10
    _exp = 0
    _lvl = 1
    _gold = 0
    _character = True
    _hp_item_bonus = 0
    _mp_item_bonus = 0
    _attack_item_bonus = 0
    _armour_item_bonus = 0

    def __init__(self):
        self._cls = 'Character'
        self._armour = 0
        self._inventory = {'Armour': None, 'Weapon': None, 'Helm': None, 'Boots': None, 'Ring': None}
        self._skills = []
        self._passives = {}
        self.recalculate_item_bonus()
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
        if hp <= self.get_maxhp():
            self._hp = hp
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
        # if charater have max hp and unequips item with bonus hp,
        # current hp is recalclated
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
            lvlup = DialogMessage('lvlup_CA', self, self.get_lvl()).get_message()
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
        self._skills.append(skill)

    def is_skill_available(self):
        """
        Returns if any of skills are available
        """
        for skill in self.get_skills():
            if skill.get_current_cd() == 0:
                return True
        return False

    def first_available_skill(self):
        """
        Cycles through character's skills and returns first spell that is ready to be used
        Skills are in order of first added
        """
        for skill in self.get_skills():
            if skill.get_current_cd() == 0:
                return skill

    def use_attack_skill(self, skill, other):
        damage = skill.get_damage()
        return DialogMessage('used_skill_C', self).get_message() + "\n" + other.take_damage_pure(damage, self)

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

    def take_damage_from(self, damage, other):
        """
        Takes damage from other character
        Prints message about that attack
        """
        self._hp -= damage * self.get_defence_modifier()
        return DialogMessage('attack_CAT', other, damage * self.get_defence_modifier(), self).get_message()  + "\n"

    def take_damage_pure(self, damage, other):
        """
        Takes pure damage from skills
        """
        self._hp -= damage
        return DialogMessage('attack_pure_CAT', other, damage, self).get_message() + "\n"

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        attack = self.get_attack() * self.get_attack_modifier()
        return other.take_damage_from(attack, self)

#   Getting character's stats #

    def get_stats(self):
        """
        Returns character's stats in a dictionary
        """
        stats = dict(CLS=self.get_class(),
                     HP=self.get_current_hp(),
                     MAX_HP=self.get_maxhp(),
                     MP=self.get_mp(),
                     ATT=round(self.get_attack_stat(), 2),
                     ATT_BONUS=round(self._attack_item_bonus, 2),
                     DEF=round(1 - self.get_defence_modifier(), 2),
                     LVL=self.get_lvl(),
                     EXP=round(self.get_exp(), 2),
                     EXPLVL=round(self.get_exp_to_next_lvl(), 2),
                     GOLD=self.get_gold(),
                     INV=self.get_inventory(),
                     SKILLS=self.get_skills(),
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
    _hp = 85
    _mp = 10
    _attack = 8

    def __init__(self):
        super().__init__()
        self._cls = 'Mage'
        self._es = self.get_es()
        self.add_skill(Fireball(self))
        self._passives['Energy Shield'] = "This passive allows Mage to absorb some of incoming damage.\n" \
                                          "ES scales with MP and lvl"

#   ES getter and setter #

    def get_es(self):
        """
        Returns character's es
        """
        return self._mp * (self.get_lvl() / 2)

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
            return DialogMessage('attack_es_CAT', other, damage, self).get_message() + "\n"
        elif 0 < self._es <= damage:
            if self._es == damage:
                self._es = 0
                return DialogMessage('broke_es_C', self).get_message() + "\n"
            else:
                leftoverdmg = damage - self._es
                self._hp -= leftoverdmg * self.get_attack_modifier()
                self._es = 0
                return DialogMessage('broke_es_dmg_hp_CAT', other, leftoverdmg * self.get_attack_modifier(), self).get_message() + "\n"
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
    _hp = 100
    hp_mult = 1.1

    def __init__(self):
        super().__init__()
        self._cls = 'Warrior'
        self._maxhp = self._hp = self.get_maxhp()
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

#   Armour passive getter #

    def get_passive_defence_bonus(self):
        """
        Returns warrior's passive defence bonus
        """
        return math.log10(self.get_maxhp() - self.get_current_hp() + 1) / 10

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
        stats['DEF_BONUS'] = round(self.get_passive_defence_bonus(), 2)
        stats['HP_BONUS'] = self.hp_mult
        return stats


class Rogue(Character):
    _crit_chance = 0.2
    _evade_chance = 0.2
    _attack = 15

    def __init__(self):
        super().__init__()
        self._cls = 'Rogue'
        self._evade_chance = self._evade_chance + 0.001 * self.get_mp()
        self._passives['Evasion'] = "This passive allows Rogue to evade some of incoming damage.\n" \
                                    "EV scales with MP"
        self._passives['Critical Strike'] = "This passive allows Rogue to double the damage some of his attacks.\n" \
                                            "Crit chance scales with MP"

#   Evasion getters and setters #

    def get_evasion(self):
        """
        Returns character's evade chance
        """
        return self._evade_chance + 0.001 * self.get_mp()

    def set_evasion(self, ev):
        """
        Sets character's evade chance
        """
        self._evade_chance = ev

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
        return self._crit_chance + 0.001 * self.get_mp()

    def set_crit_chance(self, chance):
        """
        Takes new value for character's evade chance and sets it
        """
        self._crit_chance = chance

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
        if self.get_dodge():
            return DialogMessage('evaded_CA', self, damage).get_message() + "\n"
        else:
            return super().take_damage_from(damage, other)

    def attack(self, other):
        """
        Reduces other character's hp by self's attack
        """
        if self.get_crit():
            attack = self.get_attack() * self.get_attack_modifier() * 2
            return DialogMessage('crit', self, attack).get_message() + "\n" + other.take_damage_from(attack, self)
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
        stats['CRIT_CHANCE'] = self.get_crit_chance()
        return stats


class Monster(Character):
    def __init__(self, lvl_mult=1):
        super().__init__()
        self._cls = 'Monster'
        self._lvl_mult = lvl_mult / math.sqrt(lvl_mult * 2)
        self._maxhp = (random.randint(21, 40) * self._lvl_mult)
        self._hp = self.get_maxhp()
        self._mp = (random.randint(1, 1) * self._lvl_mult)
        self._attack = (random.randint(1, 15) * self._lvl_mult)


class GreaterMonster(Monster):
    def __init__(self, lvl_mult=1):
        lvl_mult *= 2 * math.log10(lvl_mult)
        super().__init__(lvl_mult)
        self._cls = 'Greater Monster'
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self.add_item(RareItem(int(lvl_mult)))
        self._hp = self.get_maxhp()
        self._mp = self.get_mp()


class Skill:
    def __init__(self, character):
        self._owner = character
        self._cooldown = 0
        self._current_cd = 0

    def get_owner(self):
        """
        Returns skill's owner
        """
        return self._owner

    def get_name(self):
        """
        Returns skill's name
        """
        return self.__class__.__name__

    def get_cooldown_timer(self):
        """
        Returns spells's cd timer
        """
        return self._cooldown

    def set_cooldown_timer(self, cd):
        """
        Sets spells's cd timer
        """
        self._cooldown = cd

    def get_current_cd(self):
        """
        Returns spell's current cd
        """
        return self._current_cd

    def set_current_cd(self, cd):
        """
        Set new amount for current cd
        More then max cd = max cd
        Less then 0 = 0
        """
        if cd < 0:
            self._current_cd = 0
        elif cd <= self._cooldown:
            self._current_cd = cd
        else:
            self._current_cd = self._cooldown

    def is_available(self):
        """
        Returns if spell is ready to use
        """
        return self._current_cd == 0


class Fireball(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._cooldown = 5
        self._current_cd = 0

    def get_damage(self):
        """
        Returns spell's damage
        """
        return self._owner.get_mp() * 1.5