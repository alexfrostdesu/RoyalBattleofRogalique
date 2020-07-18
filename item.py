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
        name = f"{self.get_rarity()} {self.get_name()}"
        if self.get_affix():
            name += f" {self.get_affix()}"
        if self.get_prefix():
            name = f"{self.get_prefix()} " + name
        return name

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

    def get_prefix(self):
        """
        Returns item's affix
        """
        return self._item_prefix

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

    def get_unique_bonus(self):
        """
        Returns item's unique bonus
        """
        return self._unique_bonus

    @staticmethod
    def create_item_dictionary(item_bonus, player_bonus):
        """
        Creating a dictionary to create item stats
        """
        item_dict = {'Armour': [0, 2 * item_bonus, item_bonus / 2, item_bonus + player_bonus],
                     'Weapon': [item_bonus + player_bonus, 0, (item_bonus + player_bonus / 2), 0],
                     'Helm': [0, item_bonus, item_bonus / 2, item_bonus],
                     'Boots': [0, 2 * item_bonus, item_bonus / 2, item_bonus / 2],
                     'Ring': [item_bonus, 3 * item_bonus, 2 * item_bonus, item_bonus / 2]
                     }
        for k, item in item_dict.items():
            item_dict[k] = [int(i) for i in item]
        return item_dict

    def print_stats(self):
        print(self.get_full_name())
        print(f"Bonus Damage: {self._bonus_attack}")
        print(f"Bonus HP: {self._bonus_hp}")
        print(f"Bonus MP: {self._bonus_mp}")
        print(f"Bonus Defence: {self._bonus_defence}")

    def get_unique_bonus_stat(self):
        bonus_list = {'Double': 'Doubles this item main stat',
                      'Shiny': 'Boosts this item stats',
                      'Chiseled': f'All {self.get_unique_bonus()[0]} bonuses +{(self.get_unique_bonus()[1] - 1) * 100:1.1f}%',
                      'Decorated': f'All items bonuses +{(self.get_unique_bonus()[1] - 1) * 100:1.1f}%'}
        return f"```\nUnique bonus: ".ljust(
            15) + f"| {bonus_list[self.get_prefix()]}```"

    def get_stats(self):
        stats = f"*{self.get_full_name()}*\n" + \
                f"```\nBonus Damage: ".ljust(15) + f"| {self._bonus_attack}" + \
                f"\nBonus HP:".ljust(15) + f"| {self._bonus_hp}" + \
                f"\nBonus MP:".ljust(15) + f"| {self._bonus_mp}" + \
                f"\nBonus Defence:".ljust(15) + f"| {self._bonus_defence}```"
        if self.get_unique_bonus():
            stats += self.get_unique_bonus_stat()
        return stats

    def get_compare_stats(self, other_item):
        stats = f"{self.get_full_name()}\n" + \
                f"```\nBonus Damage: ".ljust(15) + f"| {self._bonus_attack}".ljust(5) + f"({self._bonus_attack - other_item.get_bonus_attack()})" + \
                f"\nBonus HP:".ljust(15) + f"| {self._bonus_hp}".ljust(5) + f"({self._bonus_hp - other_item.get_bonus_hp()})" + \
                f"\nBonus MP:".ljust(15) + f"| {self._bonus_mp}".ljust(5) + f"({self._bonus_mp - other_item.get_bonus_mp()})" + \
                f"\nBonus Defence:".ljust(15) + f"| {self._bonus_defence}".ljust(5) + f"({self._bonus_defence - other_item.get_bonus_defence()})\n```"
        if self.get_unique_bonus():
            stats += other_item.get_unique_bonus_stat()
        return stats


class CommonItem(Item):
    def __init__(self, lvl, item_type=None):
        item_bonus = 5 + lvl / 2
        player_bonus = random.randint(1, lvl)
        #                     ATTACK || HP || MP || DEFENSE
        item_dict = self.create_item_dictionary(item_bonus, player_bonus)
        if item_type:
            self._type = item_type
        else:
            self._type = random.choice(list(item_dict))
        item_stats = [random.randint(0, i) for i in item_dict[self._type]]
        self._item_affix = ''
        self._item_prefix = ''
        self._item_affix = ''
        self._unique_bonus = None
        self._rarity = 'Common'
        super().__init__(*item_stats)


class RareItem(Item):
    def __init__(self, lvl, item_type=None):
        item_bonus = 10 + lvl
        player_bonus = random.randint(0, lvl+5)
        #                     ATTACK || HP || MP || DEFENSE
        item_dict = self.create_item_dictionary(item_bonus, player_bonus)
        affixlist = ['of Damage', 'of Vitality', 'of Magic', 'of Defence', 'of Random']
        if item_type:
            self._type = item_type
        else:
            self._type = random.choice(list(item_dict))
        self._item_affix = random.choice(affixlist)
        self._rarity = 'Rare'
        self._item_prefix = ''
        self._unique_bonus = None
        item_stats = [random.randint(0, i) for i in item_dict[self._type]]
        if self._item_affix != 'of Random':
            item_stats[affixlist.index(self._item_affix)] += random.randint(0, item_bonus)
        else:
            item_stats = (random.randint(0, item_bonus), random.randint(0, item_bonus), random.randint(0, item_bonus),
                          random.randint(0, item_bonus))
        super().__init__(*item_stats)


class UniqueItem(Item):
    def __init__(self, lvl, item_type=None):
        item_bonus = 10 + lvl
        player_bonus = random.randint(0, lvl + 10)
        item_dict = self.create_item_dictionary(item_bonus, player_bonus)
        affixlist = ['of Damage', 'of Vitality', 'of Magic', 'of Defence']
        prefixlist = ['Double', 'Shiny', 'Chiseled', 'Decorated']
        stat_dict = {0: 'Attack', 1: 'HP', 2: 'MP', 3: 'Defence'}
        if item_type:
            self._type = item_type
        else:
            self._type = random.choice(list(item_dict))
        self._item_affix = random.choice(affixlist)
        self._item_prefix = random.choice(prefixlist)
        # self._item_prefix = 'Chiseled'
        self._rarity = 'Unique'
        item_stats = [random.randint(0, i) for i in item_dict[self._type]]
        if self._item_prefix == 'Double':
            item_stats[affixlist.index(self._item_affix)] += 2 * random.randint(0, item_bonus)
        else:
            item_stats[affixlist.index(self._item_affix)] += random.randint(0, item_bonus)
        if self._item_prefix == 'Shiny':
            item_stats = [int(x * 1.5) for x in item_stats]
        if self._item_prefix == 'Chiseled':
            self._unique_bonus = [stat_dict[affixlist.index(self._item_affix)], round(random.uniform(1.05, 1.05 + lvl * 0.01), 3)]
        elif self._item_prefix == 'Decorated':
            self._unique_bonus = ['All', 1.1]
        else:
            self._unique_bonus = [self._item_prefix, 0]
        super().__init__(*item_stats)


