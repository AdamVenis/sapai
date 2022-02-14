from dataclasses import dataclass
import collections
import random
from common import *


@dataclass(frozen=True)
class Ant(PetData):
    attack = 2
    health = 1
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                friends = [pet for pet in kwargs["friends"] if pet is not None]
                if friends:
                    friend = random.choice(friends)
                    friend.bonus_attack += 2 * self.level
                    friend.bonus_health += 1 * self.level


@dataclass(frozen=True)
class Beaver(PetData):
    attack = 2
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] == self:
                friends = [pet for pet in kwargs["friends"] if pet is not None]
                if len(friends) < 2:
                    for friend in friends:
                        friend.bonus_health += self.level
                else:
                    for friend in random.sample(friends, 2):
                        friend.bonus_health += self.level


@dataclass(frozen=True)
class Cricket(PetData):
    attack = 1
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                index = kwargs["index"]
                friends = kwargs["friends"]
                friends.insert(index, BattlePet(Pet(ZombieCricket())))


@dataclass(frozen=True)
class Duck(PetData):
    attack = 1
    health = 3
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] == self:
                buyable_pets = [
                    buyable
                    for buyable in kwargs["player"].shop
                    if isinstance(buyable.data, PetData)
                ]
                for pet in buyable_pets:
                    pet.bonus_health += 1


@dataclass(frozen=True)
class Fish(PetData):
    attack = 2
    health = 3
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.LEVEL_UP:
            if kwargs["source"] == self:
                for friend in kwargs["friends"]:
                    if friend is None:
                        continue
                    friend.bonus_attack += self.level - 1
                    friend.bonus_health += self.level - 1


@dataclass(frozen=True)
class Horse(PetData):
    attack = 2
    health = 1
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SUMMON:
            source = kwargs["source"]
            if source != self:
                source.battle_attack += 1


@dataclass(frozen=True)
class Mosquito(PetData):
    attack = 2
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.START_BATTLE:
            enemies = [pet for pet in kwargs["enemies"] if pet is not None]
            if enemies:
                if len(enemies) < self.level:
                    for enemy in enemies:
                        enemy.bonus_health -= 1
                else:
                    for enemy in random.sample(enemies, self.level):
                        enemy.bonus_health -= 1


@dataclass(frozen=True)
class Otter(PetData):
    attack = 1
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.BUY:
            if kwargs["source"] == self:
                friends = [
                    pet for pet in kwargs["friends"] if pet is not None and pet != self
                ]
                if friends:
                    friend = random.choice(friends)
                    friend.bonus_attack += self.level
                    friend.bonus_health += self.level


@dataclass(frozen=True)
class Pig(PetData):
    attack = 3
    health = 1
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] == self:
                kwargs["player"].money += 1


@dataclass(frozen=True)
class ZombieCricket(PetData):
    attack = 1
    health = 1
    tier = 1


@dataclass(frozen=True)
class Swan(PetData):
    attack = 1
    health = 3
    tier = 2

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Giraffe(PetData):
    attack = 2
    health = 5
    tier = 3

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Deer(PetData):
    attack = 1
    health = 1
    tier = 4

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Crocodile(PetData):
    attack = 8
    health = 4
    tier = 5

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Dragon(PetData):
    attack = 6
    health = 8
    tier = 6

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Apple(ConsumableFood):
    @staticmethod
    def consume(pet):
        pet.bonus_attack += 1
        pet.bonus_health += 1


@dataclass(frozen=True)
class Honey(EquippableFood):
    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                index = kwargs["index"]
                friends = kwargs["friends"]
                if friends[0] is None:
                    del friends[0]
                    friends.insert(index, BattlePet(Pet(HoneyBee())))


@dataclass(frozen=True)
class HoneyBee(PetData):
    attack = 1
    health = 1
    tier = 1


@dataclass(frozen=True)
class Meat(FoodData):
    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Garlic(FoodData):
    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Salad(FoodData):
    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Chocolate(FoodData):
    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Melon(FoodData):
    def effect(self):
        pass  # FIXME


def cumulative_dict(source):
    result = collections.defaultdict(list)
    keys = sorted(source.keys())
    for tier in keys:
        for i in keys:
            if i > tier:
                break
            result[tier].extend(source[i])
    return result


PACK1_PETS = {
    1: [
        Ant(),
        Beaver(),
        Cricket(),
        Duck(),
        Fish(),
        Horse(),
        Otter(),
        Pig(),
        Mosquito(),
    ],
    2: [Swan()],
    3: [Giraffe()],
    4: [Deer()],
    5: [Crocodile()],
    6: [Dragon()],
}

PACK1_FOOD = {
    1: [Apple(), Honey()],
    2: [Meat()],
    3: [Garlic()],
    4: [Salad()],
    5: [Chocolate()],
    6: [Melon()],
}

PACK1_AVAILABLE_PETS = cumulative_dict(PACK1_PETS)
PACK1_AVAILABLE_FOOD = cumulative_dict(PACK1_FOOD)
