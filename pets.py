from dataclasses import dataclass
import collections
import random
from common import *


@dataclass
class Ant(PetData):
    attack = 2
    health = 1
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                friends = kwargs["friends"]
                if friends:
                    friend = random.choice(friends)
                    friend.bonus_attack += 2 * self.level
                    friend.bonus_health += 1 * self.level


@dataclass
class Beaver(PetData):
    attack = 2
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] == self:
                friends = kwargs["friends"]
                if len(friends) < 2:
                    for friend in friends:
                        friend.bonus_health += self.level
                else:
                    for friend in random.sample(friends, 2):
                        friend.bonus_health += self.level


@dataclass
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
                if len(friends) < 5:
                    friends.insert(index, BattlePet(Pet(ZombieCricket())))
                    # FIXME - trigger summon


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
class Mosquito(PetData):
    attack = 2
    health = 2
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.START_BATTLE:
            enemies = kwargs["enemies"]
            if enemies:
                if len(enemies) < self.level:
                    for enemy in enemies:
                        take_damage(enemy, 1, enemies)
                        # FIXME - if this hits a flamingo, should the flamingo
                        # buff the ally before the second instance lands?
                else:
                    for enemy in random.sample(enemies, self.level):
                        take_damage(enemy, 1, enemies)


@dataclass
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


@dataclass
class Pig(PetData):
    attack = 3
    health = 1
    tier = 1

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] == self:
                kwargs["player"].money += 1


@dataclass
class ZombieCricket(PetData):
    attack = 1
    health = 1
    tier = 1


@dataclass
class Crab(PetData):
    attack = 3
    health = 3
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.BUY:
            if kwargs["source"] == self:
                max_friend_health = max(pet.total_health() for pet in kwargs["friends"])
                self.bonus_health = max_friend_health - 3


@dataclass
class Dodo(PetData):
    attack = 2
    health = 3
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.START_BATTLE:
            friends = kwargs["friends"]
            index = friends.index(self)
            if index < len(friends) - 1:
                friends[index + 1].bonus_attack += int(
                    self.total_attack() * 0.5 * self.level
                )


@dataclass
class Elephant(PetData):
    attack = 3
    health = 5
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.BEFORE_ATTACK:
            friends = kwargs["friends"]
            if friends[-1] == self:
                for i in range(
                    len(friends) - 2, max(-1, len(friends) - 3 - self.level), -1
                ):
                    take_damage(friends[i], 1, friends)


@dataclass
class Flamingo(PetData):
    attack = 3
    health = 1
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        pass  # FIXME


@dataclass
class Hedgehog(PetData):
    attack = 3
    health = 2
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                enemies = kwargs["enemies"]
                for enemy in enemies:
                    take_damage(enemy, 2 * self.level, enemies)
                    # FIXME - i think these instances should all land before subsequent
                    # events are emitted (like faints)


@dataclass
class Peacock(PetData):
    attack = 2
    health = 5
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.START_BATTLE:
            self.effect_charges = self.level
            # FIXME - this isn't correct. the charges should persist outside of battle.

        if event == Event.HURT:
            if kwargs["source"] == self:
                if self.effect_charges > 0:
                    self.bonus_attack += int(self.total_attack() * 0.5)
                    self.effect_charges -= 1


@dataclass
class Rat(PetData):
    attack = 4
    health = 5
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                enemies = kwargs["enemies"]
                for _ in range(self.level):
                    if len(enemies) < 5:
                        enemies.append(BattlePet(Pet(DirtyRat())))
                        # FIXME - trigger summon


@dataclass
class DirtyRat(PetData):
    attack = 1
    health = 1
    tier = 1


@dataclass
class Shrimp(PetData):
    attack = 2
    health = 3
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.SELL:
            if kwargs["source"] != self:
                friends = kwargs["friends"]
                if len(friends) < 2:
                    for friend in friends:
                        friend.bonus_health += self.level
                else:
                    for friend in random.sample(friends, 1):
                        friend.bonus_health += self.level


@dataclass
class Spider(PetData):
    attack = 2
    health = 2
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                index = kwargs["index"]
                friends = kwargs["friends"]
                if len(friends) < 5:
                    spawned_pet = BattlePet(Pet(random.choice(PACK1_PETS[3])))
                    spawned_pet.bonus_attack = 1 - spawned_pet.total_attack()
                    spawned_pet.bonus_health = 1 - spawned_pet.total_health()
                    spawned_pet.level = self.level
                    friends.insert(index, spawned_pet)
                    # FIXME - trigger summon


@dataclass
class Swan(PetData):
    attack = 1
    health = 3
    tier = 2

    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.START_ROUND:
            if kwargs["source"] == self:
                kwargs["player"].money += self.level


@dataclass
class Giraffe(PetData):
    attack = 2
    health = 5
    tier = 3

    def effect(self):
        pass  # FIXME


@dataclass
class Deer(PetData):
    attack = 1
    health = 1
    tier = 4

    def effect(self):
        pass  # FIXME


@dataclass
class Crocodile(PetData):
    attack = 8
    health = 4
    tier = 5

    def effect(self):
        pass  # FIXME


@dataclass
class Dragon(PetData):
    attack = 6
    health = 8
    tier = 6

    def effect(self):
        pass  # FIXME


@dataclass
class Apple(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        pet.bonus_attack += 1
        pet.bonus_health += 1


@dataclass
class Honey(EquippableFood):
    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.FAINT:
            if kwargs["source"] == self:
                index = kwargs["index"]
                friends = kwargs["friends"]
                if len(friends) < 5:
                    friends.insert(index, BattlePet(Pet(HoneyBee())))
                    # FIXME - trigger summon


@dataclass
class HoneyBee(PetData):
    attack = 1
    health = 1
    tier = 1


@dataclass
class Cupcake(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        pet.battle_attack += 3
        pet.battle_health += 3


@dataclass
class MeatBone(EquippableFood):
    @staticmethod
    def handle_event(self, event, **kwargs):
        if event == Event.AFTER_ATTACK:
            if kwargs["source"] == self:
                target = kwargs["target"]
                if target.total_health() >= 0:
                    take_damage(target, 5, kwargs["enemies"])


@dataclass
class SleepingPill(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        faint(pet, kwargs["friends"])


@dataclass
class Garlic(EquippableFood):
    pass


@dataclass
class Salad(ConsumableFood):
    pass


@dataclass
class Chocolate(ConsumableFood):
    pass


@dataclass
class Melon(EquippableFood):
    pass


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
        Mosquito(),
        Otter(),
        Pig(),
    ],
    2: [
        Crab(),
        Dodo(),
        Elephant(),
        Flamingo(),
        Hedgehog(),
        Peacock(),
        Rat(),
        Shrimp(),
        Spider(),
        Swan(),
    ],
    3: [Giraffe()],
    4: [Deer()],
    5: [Crocodile()],
    6: [Dragon()],
}

PACK1_FOOD = {
    1: [Apple(), Honey()],
    2: [Cupcake(), MeatBone(), SleepingPill()],
    3: [Garlic()],
    4: [Salad()],
    5: [Chocolate()],
    6: [Melon()],
}

PACK1_AVAILABLE_PETS = cumulative_dict(PACK1_PETS)
PACK1_AVAILABLE_FOOD = cumulative_dict(PACK1_FOOD)
