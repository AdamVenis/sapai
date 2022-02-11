from dataclasses import dataclass
import collections
from common import *


@dataclass(frozen=True)
class Ant(PetData):
    attack = 2
    health = 1
    tier = 1

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Horse(PetData):
    attack = 2
    health = 1
    tier = 1

    def effect(self):
        pass  # FIXME


@dataclass(frozen=True)
class Cricket(PetData):
    attack = 1
    health = 2
    tier = 1

    def effect(self):
        pass  # FIXME


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
class Apple(FoodData):
    def effect(self):
        pass  # FIXME


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
    1: [Ant(), Cricket(), Horse()],
    2: [Swan()],
    3: [Giraffe()],
    4: [Deer()],
    5: [Crocodile()],
    6: [Dragon()],
}

PACK1_FOOD = {
    1: [Apple()],
    2: [Meat()],
    3: [Garlic()],
    4: [Salad()],
    5: [Chocolate()],
    6: [Melon()],
}

PACK1_AVAILABLE_PETS = cumulative_dict(PACK1_PETS)
PACK1_AVAILABLE_FOOD = cumulative_dict(PACK1_FOOD)
