from dataclasses import dataclass
import enum

MAX_SHOP_SIZE = 7
MAX_PETS = 5


class Event(enum.Enum):
    SELF_FAINT = 0
    SUMMON = 1
    BEFORE_ATTACK = 2
    HURT = 3
    BUY = 4
    SELL = 5
    LEVEL_UP = 6
    END_TURN = 7
    START_BATTLE = 8
    KNOCKOUT = 9
    EAT = 10
    START_ROUND = 11
    AFTER_ATTACK = 12
    FRIEND_FAINT = 13


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

    def handle_event(self, event, **kwargs):
        self.data.handle_event(self, event, **kwargs)
        if self.food is not None:
            self.food.handle_event(self, event, **kwargs)

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
class PetData:
    @staticmethod
    def handle_event(self, event, **kwargs):
        # self is the pet whose effect we're checking
        pass


class ConsumableFood:
    pass


class EquippableFood:
    pass


def take_damage(pet, damage, friends, enemies):
    # print(pet, 'taking damage', damage, friends, enemies)
    pet.take_damage(damage)
    fainted = pet.total_health() <= 0

    for friend in friends:
        friend.handle_event(
            Event.HURT, source=pet, damage=damage, friends=friends, enemies=enemies
        )

    if fainted and pet in friends:
        faint(pet, friends, enemies)


def faint(pet, friends, enemies):
    index = friends.index(pet)
    del friends[index]
    pet.handle_event(
        Event.SELF_FAINT, source=pet, index=index, friends=friends, enemies=enemies
    )
    for friend in friends:
        friend.handle_event(
            Event.FRIEND_FAINT,
            source=pet,
            index=4,
            friends=friends,
        )
