import random

class Item:
    _character = False

    def __init__(self, bonus_attack=0, bonus_hp=0, bonus_mp=0, bonus_defence=0):
        self._name = self.get_type()
        self._full_name = self.get_full_name()
        self._bonus_attack = bonus_attack
        self._bonus_hp = bonus_hp
        self._bonus_mp = bonus_mp
        self._bonus_defence = bonus_defence

    def get_name(self):
        """
        Returns item's name
        """
        return self._name

    def get_full_name(self):
        """
        Returns item's name
        """
        return f"{self.get_rarity()} {self.get_name()} {self.get_affix()}"

    def set_name(self, name):
        """
        Takes new value for item's name and sets it
        """
        self._name = name

    def get_type(self):
        """
        Returns item's type
        """
        return self._type

    def get_character(self):
        """
        Check if it is a character
        """
        return self._character

    def get_rarity(self):
        """
        Returns item's type
        """
        return self._rarity

    def get_affix(self):
        """
        Returns item's affix
        """
        return self._item_affix

    def set_type(self, new_type):
        """
        Takes new value for item's type and sets it
        """
        self._name = new_type

    def get_bonus_attack(self):
        """
        Returns item's bonus attack
        """
        return self._bonus_attack

    def set_bonus_attack(self, bonus_attack):
        """
        Takes new value for item's bonus attack and sets it
        """
        self._bonus_attack = bonus_attack

    def get_bonus_hp(self):
        """
        Returns item's bonus HP
        """
        return self._bonus_hp

    def set_bonus_hp(self, bonus_hp):
        """
        Takes new value for item's bonus HP and sets it
        """
        self._bonus_hp = bonus_hp

    def get_bonus_mp(self):
        """
        Returns item's bonus MP
        """
        return self._bonus_mp

    def set_bonus_mp(self, bonus_mp):
        """
        Takes new value for item's bonus MP and sets it
        """
        self._bonus_mp = bonus_mp

    def get_bonus_defence(self):
        """
        Returns item's bonus defence
        """
        return self._bonus_defence

    def set_bonus_defence(self, bonus_defence):
        """
        Takes new value for item's bonus defence and sets it
        """
        self._bonus_defence = bonus_defence

    def print_stats(self):
        print(self.get_full_name())
        print(f"Bonus Damage: {self._bonus_attack}")
        print(f"Bonus HP: {self._bonus_hp}")
        print(f"Bonus MP: {self._bonus_mp}")
        print(f"Bonus Defence: {self._bonus_defence}")

    def get_stats(self):
        stats = f"*{self.get_full_name()}*\n" + \
                f"```\nBonus Damage: ".ljust(15) + f"| {self._bonus_attack}" + \
                f"\nBonus HP:".ljust(15) + f"| {self._bonus_hp}" + \
                f"\nBonus MP:".ljust(15) + f"| {self._bonus_mp}" + \
                f"\nBonus Defence:".ljust(15) + f"| {self._bonus_defence}```"
        return stats

    def get_compare_stats(self, other_item):
        stats = f"{self.get_full_name()}\n" + \
                f"```\nBonus Damage: ".ljust(15) + f"| {self._bonus_attack}".ljust(5) + f"({self._bonus_attack - other_item.get_bonus_attack()})" + \
                f"\nBonus HP:".ljust(15) + f"| {self._bonus_hp}".ljust(5) + f"({self._bonus_hp - other_item.get_bonus_hp()})" + \
                f"\nBonus MP:".ljust(15) + f"| {self._bonus_mp}".ljust(5) + f"({self._bonus_mp - other_item.get_bonus_mp()})" + \
                f"\nBonus Defence:".ljust(15) + f"| {self._bonus_defence}".ljust(5) + f"({self._bonus_defence - other_item.get_bonus_defence()})```"
        return stats


class CommonItem(Item):
    def __init__(self, lvl):
        player_lvl_bonus = random.randint(1, lvl)
        #                     ATTACK || HP || MP || DEFENSE
        self._item_dict = {'Armour': (0, 10, 2, 5 + player_lvl_bonus),
                     'Weapon': (5 + player_lvl_bonus, 0, 2, 0),
                     'Helm': (0, 5, 2, 5),
                     'Boots': (0, 10, 2, 2),
                     'Ring': (5, 20, 5, 0)
                           }
        self._type = random.choice(list(self._item_dict))
        item_stats = list([random.randint(0, i) for i in self._item_dict[self._type]])
        self._item_affix = ''
        self._rarity = 'Common'
        super().__init__(*item_stats)


class RareItem(Item):
    def __init__(self, lvl):
        player_lvl_bonus = random.randint(0, lvl+3)
        #                     ATTACK || HP || MP || DEFENSE
        self._item_dict = {'Armour': (0, 40, 10, 15 + player_lvl_bonus),
                           'Weapon': (15 + player_lvl_bonus, 0, 10, 0),
                           'Helm': (0, 10, 10, 5),
                           'Boots': (0, 20, 4, 4),
                           'Ring': (10, 20, 20, 0)
                           }
        self._affixlist = ['of Damage', 'of Vitality', 'of Magic', 'of Defence', 'of Random']
        self._type = random.choice(list(self._item_dict))
        self._item_affix = random.choice(self._affixlist)
        self._rarity = 'Rare'
        item_stats = list([random.randint(0, i) for i in self._item_dict[self._type]])
        if self._item_affix != 'of Random':
            item_stats[self._affixlist.index(self._item_affix)] += player_lvl_bonus
        else:
            item_stats = (random.randint(0, 10), random.randint(0, 30), random.randint(0, 10), random.randint(0, 10))
        super().__init__(*item_stats)
