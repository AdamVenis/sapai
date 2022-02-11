from dataclasses import dataclass
import collections

class PetData:
    pass

class FoodData:
    pass

@dataclass(frozen=True)
class Ant(PetData):
    attack = 2
    health = 1
    tier = 1
    def effect(self):
        pass # FIXME

@dataclass(frozen=True)
class Horse(PetData):
    attack = 2
    health = 1
    tier = 1
    def effect(self):
        pass # FIXME

@dataclass(frozen=True)
class Cricket(PetData):
    attack = 1
    health = 2
    tier = 1
    def effect(self):
        pass # FIXME

@dataclass(frozen=True)
class Apple(FoodData):
    def effect(self):
        pass # FIXME


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
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
}

PACK1_FOOD = {
    1: [Apple()],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
}

PACK1_AVAILABLE_PETS = cumulative_dict(PACK1_PETS)
PACK1_AVAILABLE_FOOD = cumulative_dict(PACK1_FOOD)
    