from dataclasses import dataclass
import enum
import copy
import random

import pets
from common import *


def empty_effect():
    pass


# possible actions:
# end turn
# buy [pet/food] - requires index * target
# reposition - requires from_index * to_index
# sell pet - requires index
# combine pet - requires index * target
# roll


class Action:
    def act(self):
        pass


@dataclass
class EndTurn:
    def valid(self, player, game):
        return True


@dataclass
class Buy:
    source_index: int
    target_index: int

    def valid(self, player, game):
        player = game.players[game.current_player_index]
        if self.source_index >= len(player.shop):
            return False
        # invalid target
        # not enough money
        return True  # FIXME

    def act(self, player, game):
        player = game.players[game.current_player_index]
        player.money -= 3  # FIXME
        purchased = player.shop[self.source_index]
        if isinstance(purchased.data, PetData):
            player.pets[self.target_index] = Pet(purchased.data)
            # add a pet in target location FIXME
        else:
            # attach food to pet in target location FIXME
            pass


@dataclass
class Reposition:
    source_index: int
    target_index: int

    def valid(self, player, game):
        return (
            player.pets[self.source_index] is not None
            and self.source_index != self.target_index
        )

    def act(self, player, game):
        source_pet = player.pets[self.source_index]
        delta = 1 if self.target_index > self.source_index else -1
        for i in range(self.source_index, self.target_index, delta):
            player.pets[i] = player.pets[i + delta]

        player.pets[self.target_index] = source_pet


@dataclass
class Sell:
    index: int

    def valid(self, player, game):
        return player.pets[self.index] is not None

    def act(self, player, game):
        player.pets[self.index] = None
        player.money += 1  # FIXME


@dataclass
class Roll:
    def valid(self, player, game):
        return player.money >= 1

    def act(self, player, game):
        player.money -= 1
        player.refresh_shop(game.round)


@dataclass
class Combine:
    source_index: int
    target_index: int

    def valid(self, player, game):
        pet1, pet2 = player.pets[self.source_index], player.pets[self.target_index]
        if pet1 is None:
            return False
        if pet2 is None:
            return False
        return pet1.data == pet2.data

    def act(self, player, game):
        player.pets[self.source_index] = None  # FIXME


# add some pets here (there are 80 lol)
class Pet:
    def __init__(self, pet_data):
        self.attack = pet_data.attack
        self.health = pet_data.health
        self.tier = pet_data.tier
        self.data = pet_data
        self.food = None
        self.effect = empty_effect


class Food:
    def __init__(self, food_data):
        self.food_data = food_data


class Player:
    def __init__(self, health):
        self.pets = [None] * 5
        self.shop = []
        self.money = 0
        self.health = health

    def get_pets_for_battle(self):
        return [copy.copy(pet) for pet in self.pets if pet is not None]

    def refresh_shop(self, round):
        # seems to be uniform with replacement among all available pets
        new_pet_shop = []
        new_food_shop = []
        for buyable in self.shop:
            if buyable is None:
                continue

            if buyable.frozen:
                if isinstance(buyable.data, PetData):
                    new_pet_shop.append(buyable)
                else:
                    new_food_shop.append(buyable)

        tier = current_tier(round)

        max_buyable_pets = 3  # FIXME
        max_buyable_food = min(MAX_SHOP_SIZE, max_buyable_pets - 2)  # FIXME

        while len(new_pet_shop) < max_buyable_pets:
            new_pet = random.choice(pets.PACK1_AVAILABLE_PETS[tier])
            new_pet_shop.append(Buyable(new_pet))

        while len(new_food_shop) < max_buyable_food:
            new_food = random.choice(pets.PACK1_AVAILABLE_FOOD[tier])
            new_food_shop.append(Buyable(new_food))

        self.shop = new_pet_shop + new_food_shop


class Buyable:
    def __init__(self, pet_or_food_data):
        self.data = pet_or_food_data
        self.frozen = False


class BattleResult(enum.Enum):
    WIN = 1
    DRAW = 2
    LOSS = 3


class GameResult(enum.Enum):
    UNFINISHED = 0
    P1_WIN = 1
    P2_WIN = 2


# main loop
class Game:
    def __init__(self):
        self.p1, self.p2 = Player(10), Player(10)
        self.players = [self.p1, self.p2]
        self.round = 1
        self.result = GameResult.UNFINISHED
        self.current_player_index = 0
        self.start_round()

    def check_result(self):
        if self.p2.health <= 0:
            self.result = GameResult.P1_WIN
        if self.p1.health <= 0:
            self.result = GameResult.P2_WIN

    def start_round(self):
        for player in self.players:
            player.refresh_shop(self.round)
            player.money = 10

    def finish_round(self):
        battle_result = resolve_battle(self.p1, self.p2)
        # print(self.round, self.p1.health, self.p2.health, battle_result)
        if battle_result == BattleResult.WIN:
            lose_round(self.p2, self.round)
        elif battle_result == BattleResult.LOSS:
            lose_round(self.p1, self.round)

    def current_player(self):
        return self.players[self.current_player_index]

    def step(self, action):
        self.check_result()
        if self.result != GameResult.UNFINISHED:
            return self.result

        if type(action) == EndTurn:
            self.current_player_index = (self.current_player_index + 1) % 2
            if self.current_player_index == 0:
                self.finish_round()
                self.round += 1
                self.start_round()
        else:
            action.act(self.current_player(), self)

        return self.result


def current_tier(round):
    if round < 3:
        return 1
    elif round < 5:
        return 2
    elif round < 7:
        return 3
    elif round < 9:
        return 4
    elif round < 11:
        return 5
    return 6


def lose_round(player, round):
    if round < 4:
        player.health -= 1
    elif round < 6:
        player.health -= 2
    else:
        player.health -= 3


def resolve_battle(p1, p2):
    p1_pets = p1.get_pets_for_battle()
    p2_pets = p2.get_pets_for_battle()
    while p1_pets and p2_pets:
        p1_pets[-1].health -= p2_pets[-1].attack
        p2_pets[-1].health -= p1_pets[-1].attack
        if p1_pets[-1].health <= 0:
            p1_pets.pop()
        if p2_pets[-1].health <= 0:
            p2_pets.pop()

    if p1_pets:
        return BattleResult.WIN
    elif p2_pets:
        return BattleResult.LOSS
    else:
        return BattleResult.DRAW
