from classes import *
import math
import random


class Skill:
    def __init__(self, character):
        self._cooldown = 0
        self._current_cd = 0
        self._name = 'Skill'
        self._owner_stats = character.get_stats()

    def get_name(self):
        """
        Returns skill's name
        """
        return self._name

    def get_owner_stats(self):
        """
        Returns owner's stats currently stored in spell
        """
        return self._owner_stats

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

    def update_skill(self, character):
        """
        Updates skill stats
        """
        self._owner_stats = character.get_stats()

    def reset(self):
        """
        Resets skill to its default state
        Does nothing for this spell
        """
        pass

# Attack Skills #


class Fireball(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._name = 'Fireball'
        self._cooldown = 4

    def get_damage(self):
        """
        Returns spell's damage
        """
        return self.get_owner_stats()['MP'] * 1.5

    def use_skill(self, target):
        """
        Use Fireball on target
        """
        self.set_current_cd(self.get_cooldown_timer())
        output = DialogMessage('used_skill_C',
                               {'char': self.get_owner_stats()['CLS'], 'skill': self.get_name()}).get_message() + "\n"
        output += target.take_damage(self.get_damage(), self.get_owner_stats()['CLS'])
        return output


class VoidStrike(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._name = 'Void Strike'
        self._cooldown = 3

    def get_damage(self):
        """
        Returns spell's damage
        """
        return self._owner_stats['ATT']

    def use_skill(self, target):
        """
        Use VoidStrike on target
        """
        self.set_current_cd(self.get_cooldown_timer())
        output = DialogMessage('used_skill_C',
                               {'char': self.get_owner_stats()['CLS'], 'skill': self.get_name()}).get_message() + "\n"
        output += target.take_damage_pure(self.get_damage(), self.get_owner_stats()['CLS'])
        return output


class CriticalStrike(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._name = 'Critical Strike'
        self._crit_mult = 2
        self._crit_chance = 0.15
        self._cooldown = 0

    def get_damage(self):
        """
        Returns spell's damage
        """
        return (self.get_owner_stats()['ATT'] + self.get_owner_stats()['ATT_BONUS']) * self.get_crit_mult()

    def get_crit_chance(self):
        """
        Returns spell's crit chance
        """
        return self._crit_chance + 0.001 * self.get_owner_stats()['MP']

    def get_crit_mult(self):
        """
        Returns spell's crit multiplier
        """
        return self._crit_mult

    def set_crit_mult(self, amount):
        """
        Sets spell's crit multiplier to amount
        Can't be set lower than 1
        """
        if amount >= 1:
            self._crit_mult = amount
        else:
            self._crit_mult = 1

    def set_crit_chance(self, amount):
        """
        Sets spell's default crit chance to amount
        Can't be set lower than 0
        """
        if amount >= 0:
            self._crit_chance = amount
        else:
            self._crit_chance = 0

    def is_available(self):
        """
        Returns if spell is ready to use
        """
        return random.random() < self.get_crit_chance()

    def use_skill(self, target):
        """
        Use critical strike on target
        """
        output = DialogMessage('crit',
                               {'char': self.get_owner_stats()['CLS'], 'skill': self.get_name()}).get_message() + "\n"
        output += target.take_damage(self.get_damage(), self.get_owner_stats()['CLS'])
        return output


# Defence Skills #


class EnergyShield(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._es = self.get_max_es()
        self._name = 'Energy Shield'
        self._leftoverdamage = 0

    def get_max_es(self):
        """
        Returns skill's max es
        """
        return self._owner_stats['MP'] * math.sqrt(self.get_owner_stats()['LVL'] * 2)

    def get_es(self):
        """
        Returns current es
        """
        return self._es

    def get_leftoverdamage(self):
        """
        Returns leftover damage
        """
        return self._leftoverdamage

    def reset(self):
        """
        Resets es meter to character's mp
        """
        self._es = self.get_max_es()

    def is_available(self):
        """
        Returns if spell is ready to use
        """
        return self.get_es() > 0

    def use_skill(self, damage, attacker):
        """
        Takes other character's attack and reduces self es or/and hp by it
        Prints message about that attack
        """
        if damage < self.get_es():
            self._es -= damage
            return DialogMessage('attack_es_CAT', {'char': attacker, 'amount': damage,
                                                   'target': self.get_owner_stats()['CLS']}).get_message() + "\n"
        else:
            if self.get_es() == damage:
                self._es = 0
                return DialogMessage('attack_es_CAT', {'char': attacker, 'amount': damage,
                                                       'target': self.get_owner_stats()['CLS']}).get_message() + "\n" + \
                        DialogMessage('broke_es_C', {'char': self.get_owner_stats()['CLS']}).get_message() + "\n"
            else:
                self._leftoverdamage = damage - self.get_es()
                es_damage = self.get_es()
                self._es = 0
                return DialogMessage('attack_es_CAT', {'char': attacker, 'amount': es_damage,
                                                       'target': self.get_owner_stats()['CLS']}).get_message() + "\n" + \
                       DialogMessage('broke_es_C', {'char': self.get_owner_stats()['CLS']}).get_message() + "\n"


class Evasion(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._name = 'Evasion'
        self._evasion_chance = 0.15
        self._leftoverdamage = 0

    def get_leftoverdamage(self):
        """
        Returns leftover damage
        """
        return self._leftoverdamage

    def get_evasion_chance(self):
        """
        Returns spell's evasion chance
        """
        return self._evasion_chance + 0.001 * self.get_owner_stats()['MP']

    def set_evasion_chance(self, amount):
        """
        Sets spell's default evasion chance to amount
        Can't be set lower than 0
        """
        if amount >= 0:
            self._evasion_chance = amount
        else:
            self._evasion_chance = 0

    def is_available(self):
        """
        Returns if spell is ready to use
        """
        return random.random() < self.get_evasion_chance()

    def use_skill(self, damage, attacker=None):
        """
        Evades attack
        Prints message about that attack
        """
        return DialogMessage('evaded_CA', {'char': self.get_owner_stats()['CLS'], 'amount': damage}).get_message() + "\n"


class WarriorBlood(Skill):
    def __init__(self, character):
        super().__init__(character)
        self._name = 'Warrior Blood'
        self._leftoverdamage = 0
        self._defence_bonus = self.get_defence_bonus()

    def get_leftoverdamage(self):
        """
        Returns leftover damage
        """
        return self._leftoverdamage

    def get_defence_bonus(self):
        """
        Returns defence bonus HP/MaxHP
        """
        hp_bonus = (self.get_owner_stats()['HP']/self.get_owner_stats()['MAX_HP'])/100
        return math.sqrt(hp_bonus)

    def update_skill(self, character):
        """
        Updates skill stats
        """
        super().update_skill(character)
        self._leftoverdamage = 0

    def use_skill(self, damage, attacker=None):
        """
        Takes damage and reduces it by defence bonus
        """
        self._leftoverdamage = damage * (1 - self.get_defence_bonus())
        print(damage, self._leftoverdamage)
        return ''

