from dataclasses import dataclass
import enum
import typing

MAX_SHOP_SIZE = 7
MAX_PETS = 5


@dataclass
class PetData:
    def handle_event(self, event):
        pass


class Food:
    pass


class ConsumableFood(Food):
    @staticmethod
    def consume(pet, **kwargs):
        pass


class EquippableFood(Food):
    def handle_event(self, event):
        pass


class Pet:
    def __init__(self, data):
        self.data = data
        self.attack = data.attack
        self.health = data.health
        self.tier = data.tier
        self.bonus_attack = 0
        self.bonus_health = 0
        self.battle_attack = 0  # expires at the beginning of next round
        self.battle_health = 0
        self.effect_charges = 0
        self.level = 1
        self.copies = 1
        self.food = None

    def to_battle_pet(self):
        pet = Pet(self.data)
        pet.bonus_attack = self.bonus_attack
        pet.bonus_health = self.bonus_health
        pet.battle_attack = self.battle_attack
        pet.battle_health = self.battle_health
        pet.level = self.level
        pet.copies = self.copies
        pet.food = self.food
        return pet

    def total_attack(self):
        return self.attack + self.copies - 1 + self.bonus_attack + self.battle_attack

    def total_health(self):
        return self.health + self.copies - 1 + self.bonus_health + self.battle_health

    def take_damage(self, damage):
        self.bonus_health -= damage

    def handle_event(self, event):
        self.data.handle_event(event)
        if self.food is not None:
            self.food.handle_event(event)

    def combine(self, other):
        self.copies += 1

        if self.copies == 3:
            self.level = 2
            level_up = True
        elif self.copies == 6:
            self.level = 3
            level_up = True
        else:
            level_up = False

        self.bonus_attack = max(self.bonus_attack, other.bonus_attack)
        self.bonus_health = max(self.bonus_health, other.bonus_health)

        if self.food is None:
            self.food = other.food

        return level_up

    def __repr__(self):
        food_repr = f", {self.food.__class__.__name__}" if self.food is not None else ""
        return f"{self.data.__class__.__name__}({self.total_attack()}, {self.total_health()}{food_repr})"


@dataclass
class SelfFaintEvent:
    self: Pet
    index: int
    friends: list
    enemies: list


@dataclass
class SummonEvent:
    self: Pet
    source: Pet
    friends: list


@dataclass
class BeforeAttackEvent:
    self: Pet
    friends: list
    enemies: list


@dataclass
class HurtEvent:
    self: Pet
    source: Pet
    damage: int
    friends: list
    enemies: list


@dataclass
class BuyEvent:
    self: Pet
    source: Pet
    friends: list
    lost_last_turn: bool


@dataclass
class SellEvent:
    self: Pet
    source: Pet
    friends: list
    player: typing.Any  # FIXME - actually a Player but annoying to fix


@dataclass
class LevelUpEvent:
    self: Pet
    source: Pet
    friends: list


@dataclass
class EndTurnEvent:
    self: Pet
    friends: list


@dataclass
class StartBattleEvent:
    self: Pet
    friends: list
    enemies: list


@dataclass
class EatEvent:
    self: Pet
    food: Food
    target: Pet


@dataclass
class StartRoundEvent:
    self: Pet
    player: typing.Any


@dataclass
class AfterAttackEvent:
    self: Pet
    source: Pet
    target: Pet
    friends: list
    enemies: list


@dataclass
class FriendFaintEvent:
    self: Pet
    source: Pet
    index: int
    friends: list
    enemies: list


def take_damage(pet, damage, friends, enemies):
    # print(pet, 'taking damage', damage, friends, enemies)
    pet.take_damage(damage)
    fainted = pet.total_health() <= 0

    for friend in friends:
        friend.handle_event(HurtEvent(friend, pet, damage, friends, enemies))

    if fainted and pet in friends:
        faint(pet, friends, enemies)


def faint(pet, friends, enemies):
    index = friends.index(pet)
    del friends[index]
    pet.handle_event(SelfFaintEvent(pet, index, friends, enemies))

    for friend in friends:
        friend.handle_event(FriendFaintEvent(friend, pet, index, friends, enemies))
