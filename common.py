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


class PetData:
    @staticmethod
    def handle_event(self, event, source, player, game, **kwargs):
        pass


class FoodData:
    @staticmethod
    def handle_event(self, event, source, player, game, **kwargs):
        pass
