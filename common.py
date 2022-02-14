import enum

MAX_SHOP_SIZE = 7
MAX_PETS = 5


class Event(enum.Enum):
    FAINT = 0
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


class Pet:
    def __init__(self, pet_data):
        self.bonus_attack = 0
        self.battle_attack = 0  # expires at the beginning of next round
        self.bonus_health = 0
        self.battle_health = 0
        self.tier = pet_data.tier
        self.level = 1
        self.copies = 1
        self.data = pet_data
        self.food = None

    def total_attack(self):
        return (
            self.data.attack + self.copies - 1 + self.bonus_attack + self.battle_attack
        )

    def total_health(self):
        return (
            self.data.health + self.copies - 1 + self.bonus_health + self.battle_health
        )

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

        self.attack = (
            self.data.attack
            + self.copies
            - 1
            + max(self.bonus_attack, other.bonus_attack)
        )
        self.health = (
            self.data.health
            + self.copies
            - 1
            + max(self.bonus_health, other.bonus_health)
        )
        if self.food is None:
            self.food = other.food

        return level_up

    def __repr__(self):
        return f"{self.data.__class__.__name__}({self.total_attack()}, {self.total_health()})"


class BattlePet:
    def __init__(self, pet):
        self.attack = pet.total_attack()
        self.bonus_attack = 0
        self.health = pet.total_health()
        self.bonus_health = 0
        self.level = pet.level
        self.data = pet.data
        self.food = pet.food

    def total_attack(self):
        return self.attack + self.bonus_attack

    def total_health(self):
        return self.health + self.bonus_health

    def take_damage(self, damage):
        self.bonus_health -= damage
        # FIXME - this needs to trigger a faint if appropriate

    def handle_event(self, event, **kwargs):
        self.data.handle_event(self, event, **kwargs)
        if self.food is not None:
            self.food.handle_event(self, event, **kwargs)

    def __repr__(self):
        return f"{self.data.__class__.__name__}({self.total_attack()}, {self.total_health()})"


class PetData:
    @staticmethod
    def handle_event(self, event, **kwargs):
        pass


class FoodData:
    @staticmethod
    def handle_event(self, event, **kwargs):
        pass


class ConsumableFood:
    pass


class EquippableFood:
    pass
