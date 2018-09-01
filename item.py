import random


class Item:
    def __init__(self, item_name, bonus_attack=0, bonus_hp=0, bonus_mp=0, bonus_defence=0):
        self._name = item_name
        self._bonus_attack = bonus_attack
        self._bonus_hp = bonus_hp
        self._bonus_mp = bonus_mp
        self._bonus_defence = bonus_defence

    def get_name(self):
        """
        Returns item's name
        """
        return self._name

    def set_name(self, name):
        """
        Takes new value for item's name and sets it
        """
        self._name = name

    def get_type(self):
        return self._type

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
        print(self._name)
        print(f"Bonus Damage: {self._bonus_attack}")
        print(f"Bonus HP: {self._bonus_hp}")
        print(f"Bonus MP: {self._bonus_mp}")
        print(f"Bonus Defence: {self._bonus_defence}")


class CommonItem(Item):
    def __init__(self):
        player_lvl_bonus = random.randint(1, 1)  # playerchar.getlvl())
        item_dict = {'Armor': (0, random.randint(0, 10), random.randint(0, 10), random.randint(0, 5) + player_lvl_bonus),
                     'Weapon': (random.randint(0, 5), 0, 0, 0),
                     'Helm': (0, random.randint(0, 5), random.randint(0, 5), random.randint(0, 3) + player_lvl_bonus),
                     'Boots': (0, random.randint(0, 5), random.randint(0, 0), random.randint(0, 2) + player_lvl_bonus),
                     'Ring': (random.randint(0, 5), random.randint(0, 20), random.randint(0, 20), 0)
                     }
        item_name = self._type = random.choice(list(item_dict))
        item_stats = item_dict[item_name]
        item_name = "Common " + item_name
        super().__init__(item_name, *item_stats)


# item_dict = {'Armor': None,
#              'Weapon': None,
#              'Helm': None,
#              'Boots': None,
#              'Ring': None}
# item_name = random.choice(list(item_dict))
# print(item_name)
# print(item_dict[item_name])
