from dataclasses import dataclass
import collections
import random
from common import *


@dataclass
class Ant(PetData):
    attack = 2
    health = 1
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if event.friends:
                friend = random.choice(event.friends)
                friend.bonus_attack += 2 * event.self.level
                friend.bonus_health += 1 * event.self.level


@dataclass
class Beaver(PetData):
    attack = 2
    health = 2
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SellEvent):
            if event.source == event.self:
                for friend in random.sample(event.friends, min(2, len(event.friends))):
                    friend.bonus_health += event.self.level


@dataclass
class Cricket(PetData):
    attack = 1
    health = 2
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if len(event.friends) < 5:
                event.friends.insert(event.index, Pet(ZombieCricket()))
                # FIXME - trigger summon


@dataclass
class Duck(PetData):
    attack = 1
    health = 3
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SellEvent):
            if event.source == event.self:
                buyable_pets = [
                    buyable
                    for buyable in event.player.shop
                    if isinstance(buyable.data, PetData)
                ]
                for pet in buyable_pets:
                    pet.bonus_health += 1


@dataclass
class Fish(PetData):
    attack = 2
    health = 3
    tier = 1

    def handle_event(self, event):
        if isinstance(event, LevelUpEvent):
            if event.source == event.self:
                for friend in event.friends:
                    friend.bonus_attack += event.self.level - 1
                    friend.bonus_health += event.self.level - 1


@dataclass
class Horse(PetData):
    attack = 2
    health = 1
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SummonEvent):
            if event.source != event.self:
                event.source.battle_attack += 1


@dataclass
class Mosquito(PetData):
    attack = 2
    health = 2
    tier = 1

    def handle_event(self, event):
        if isinstance(event, StartBattleEvent):
            if event.enemies:
                for enemy in random.sample(event.enemies, min(event.self.level, len(event.enemies))):
                    take_damage(enemy, 1, event.enemies, event.friends)
                    # FIXME - if this hits a flamingo, should the flamingo
                    # buff the ally before the second instance lands?


@dataclass
class Otter(PetData):
    attack = 1
    health = 2
    tier = 1

    def handle_event(self, event):
        if isinstance(event, BuyEvent):
            if event.source == event.self:
                friends = [pet for pet in event.friends if pet != event.self]
                if friends:
                    friend = random.choice(friends)
                    friend.bonus_attack += event.self.level
                    friend.bonus_health += event.self.level


@dataclass
class Pig(PetData):
    attack = 3
    health = 1
    tier = 1

    def handle_event(self, event):
        if isinstance(event, SellEvent):
            if event.source == event.self:
                event.player.money += 1


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

    def handle_event(self, event):
        if isinstance(event, BuyEvent):
            if event.source == event.self:
                max_friend_health = max(pet.total_health() for pet in event.friends)
                event.self.bonus_health = max_friend_health - 3


@dataclass
class Dodo(PetData):
    attack = 2
    health = 3
    tier = 2

    def handle_event(self, event):
        if isinstance(event, StartBattleEvent):
            index = event.friends.index(event.self)
            if index < len(event.friends) - 1:
                event.friends[index + 1].bonus_attack += int(
                    event.self.total_attack() * 0.5 * event.self.level
                )


@dataclass
class Elephant(PetData):
    attack = 3
    health = 5
    tier = 2

    def handle_event(self, event):
        if isinstance(event, BeforeAttackEvent):
            if event.friends[-1] == event.self:
                for i in range(event.self.level):
                    if len(event.friends) - 2 - i >= 0:
                        take_damage(
                            event.friends[-2 - i], 1, event.friends, event.enemies
                        )


@dataclass
class Flamingo(PetData):
    attack = 3
    health = 1
    tier = 2

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if event.friends:
                for i in range(2):
                    if event.index - 1 - i >= 0:
                        event.friends[event.index - 1 - i].bonus_attack += event.self.level
                        event.friends[event.index - 1 - i].bonus_health += event.self.level


@dataclass
class Hedgehog(PetData):
    attack = 3
    health = 2
    tier = 2

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if event.enemies is None:
                return
            for enemy in event.enemies:
                take_damage(enemy, 2 * event.self.level, event.enemies, event.friends)
                # FIXME - i think these instances should all land before subsequent
                # events are emitted (like faints)


@dataclass
class Peacock(PetData):
    attack = 2
    health = 5
    tier = 2

    def handle_event(self, event):
        if isinstance(event, StartBattleEvent):
            event.self.effect_charges = event.self.level
            # FIXME - this isn't correct. the charges should persist outside of battle.

        if isinstance(event, HurtEvent):
            if event.source == event.self:
                if event.self.effect_charges > 0:
                    event.self.bonus_attack += int(event.self.total_attack() * 0.5)
                    event.self.effect_charges -= 1


@dataclass
class Rat(PetData):
    attack = 4
    health = 5
    tier = 2

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if event.enemies is None:
                return
            for _ in range(event.self.level):
                if len(event.enemies) < 5:
                    event.enemies.append(Pet(DirtyRat()))
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

    def handle_event(self, event):
        if isinstance(event, SellEvent):
            if event.source != event.self:
                for friend in random.sample(event.friends, min(1, len(event.friends))):
                    friend.bonus_health += event.self.level


@dataclass
class Spider(PetData):
    attack = 2
    health = 2
    tier = 2

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if len(event.friends) < 5:
                spawned_pet = Pet(random.choice(PACK1_PETS[3]))
                spawned_pet.bonus_attack = 1 - spawned_pet.total_attack()
                spawned_pet.bonus_health = 1 - spawned_pet.total_health()
                spawned_pet.level = event.self.level
                event.friends.insert(event.index, spawned_pet)
                # FIXME - trigger summon


@dataclass
class Swan(PetData):
    attack = 1
    health = 3
    tier = 2

    def handle_event(self, event):
        if isinstance(event, StartRoundEvent):
            event.player.money += event.self.level


@dataclass
class Badger(PetData):
    attack = 5
    health = 4
    tier = 3

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if event.index > 0:
                take_damage(
                    event.friends[event.index - 1],
                    event.self.total_attack() * event.self.level,
                    event.friends,
                    event.enemies,
                )
            if event.index == len(event.friends) and event.enemies is not None:
                for enemy in reversed(event.enemies):
                    if enemy.total_health() > 0:
                        take_damage(
                            enemy,
                            event.self.total_attack() * event.self.level,
                            event.enemies,
                            event.friends,
                        )
                        break
            elif event.index + 1 < len(event.friends):
                take_damage(
                    event.friends[event.index + 1],
                    event.self.total_attack() * event.self.level,
                    event.friends,
                    event.enemies,
                )


@dataclass
class Blowfish(PetData):
    attack = 3
    health = 5
    tier = 3

    def handle_event(self, event):
        if isinstance(event, HurtEvent):
            if event.source == event.self:
                if event.enemies:
                    random_enemy = random.choice(event.enemies)
                    take_damage(
                        random_enemy, 2 * event.self.level, event.enemies, event.friends
                    )


@dataclass
class Camel(PetData):
    attack = 2
    health = 5
    tier = 3

    def handle_event(self, event):
        if isinstance(event, HurtEvent):
            if event.source == event.self:
                index = event.friends.index(event.self)
                if index > 0:
                    event.friends[index - 1].bonus_attack += event.self.level
                    event.friends[index - 1].bonus_health += 2 * event.self.level


@dataclass
class Dog(PetData):
    attack = 2
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, SummonEvent):
            if event.source != event.self:
                if random.random() < 0.5:
                    event.self.bonus_attack += event.self.level
                else:
                    event.self.bonus_health += event.self.level


@dataclass
class Giraffe(PetData):
    attack = 2
    health = 5
    tier = 3

    def handle_event(self, event):
        if isinstance(event, EndTurnEvent):
            index = event.friends.index(event.self)
            for i in range(event.self.level):
                if index + 1 + i < len(event.friends):
                    event.friends[index + 1 + i].bonus_attack += 1
                    event.friends[index + 1 + i].bonus_health += 1


@dataclass
class Kangaroo(PetData):
    attack = 1
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, AfterAttackEvent):
            source_index = event.friends.index(event.source)
            self_index = event.friends.index(event.self)

            if source_index == self_index + 1:
                event.self.bonus_attack += 2 * event.self.level
                event.self.bonus_health += 2 * event.self.level



@dataclass
class Ox(PetData):
    attack = 1
    health = 4
    tier = 3

    def handle_event(self, event):
        if isinstance(event, FriendFaintEvent):
            if event.friends.index(event.self) == event.index - 1:
                event.self.bonus_attack += 2 * event.self.level
                event.self.food = Melon()



@dataclass
class Rabbit(PetData):
    attack = 3
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, EatEvent):
            if event.target != event.self:
                event.target.bonus_health += event.self.level


@dataclass
class Sheep(PetData):
    attack = 2
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            for _ in range(2):
                if len(event.friends) < 5:
                    event.friends.insert(event.index, Pet(Ram()))
                    # FIXME - trigger summon


@dataclass
class Ram(PetData):
    attack = 2
    health = 2
    tier = 3


@dataclass
class Snail(PetData):
    attack = 2
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, BuyEvent):
            if event.source == event.self:
                if event.lost_last_turn:
                    for pet in event.friends:
                        if pet == event.self:
                            continue
                        pet.bonus_attack += event.self.level
                        pet.bonus_health += event.self.level


@dataclass
class Turtle(PetData):
    attack = 1
    health = 2
    tier = 3

    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if 0 <= event.index - 1 < len(event.friends):
                event.friends[event.index - 1].food = Melon()


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
    def handle_event(self, event):
        if isinstance(event, SelfFaintEvent):
            if len(event.friends) < 5:
                event.friends.insert(event.index, Pet(HoneyBee()))
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
    def handle_event(self, event):
        if isinstance(event, AfterAttackEvent):
            if event.source == event.self:
                if event.target.total_health() >= 0:
                    take_damage(event.target, 5, event.enemies, event.friends)


@dataclass
class SleepingPill(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        faint(pet, friends=kwargs["friends"], enemies=None)


@dataclass
class Garlic(EquippableFood):
    pass


@dataclass
class Salad(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        pass


@dataclass
class Chocolate(ConsumableFood):
    @staticmethod
    def consume(pet, **kwargs):
        pass


@dataclass
class Melon(EquippableFood):
    def handle_event(self, event):
        if isinstance(event, HurtEvent):
            if event.source == event.self:
                damage_reduction = min(event.damage, 20)
                event.self.bonus_health += damage_reduction
                event.self.food = None


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
    3: [
        Badger(),
        Blowfish(),
        Camel(),
        Dog(),
        Giraffe(),
        Kangaroo(),
        Ox(),
        Rabbit(),
        Sheep(),
        Snail(),
        Turtle(),
    ],
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
