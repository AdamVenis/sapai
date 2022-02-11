from dataclasses import dataclass
import enum
import copy
import random

import pets
from common import *


def empty_effect():
    pass


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
        if player.money < 3:  # FIXME
            return False

        purchased = player.shop[self.source_index]
        target_pet = player.pets[self.target_index]
        if isinstance(purchased.data, PetData):
            if target_pet is not None:
                if target_pet.level == 3 or target_pet.data != purchased.data:
                    return False
        else:
            if target_pet is None:
                return False
        return True

    def act(self, player, game):
        player = game.players[game.current_player_index]
        player.money -= 3  # FIXME
        purchased = player.shop[self.source_index]
        target_pet = player.pets[self.target_index]
        if isinstance(purchased.data, PetData):
            new_pet = Pet(purchased.data)
            if target_pet is not None:
                bonus_unit = target_pet.combine(new_pet)
                if bonus_unit:
                    player.add_bonus_unit(game.round)
            else:
                player.pets[self.target_index] = new_pet
        else:
            target_pet.food = purchased.data


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
        target_pet = player.pets[self.target_index]
        bonus_unit = target_pet.combine(player.pets[self.source_index])
        if bonus_unit:
            player.add_bonus_unit(game.round)
        player.pets[self.source_index] = None


class Pet:
    def __init__(self, pet_data):
        self.bonus_attack = 0
        self.bonus_health = 0
        self.tier = pet_data.tier
        self.level = 1
        self.copies = 1
        self.data = pet_data
        self.food = None
        self.effect = empty_effect

    def total_attack(self):
        return self.data.attack + self.copies - 1 + self.bonus_attack

    def total_health(self):
        return self.data.health + self.copies - 1 + self.bonus_health

    def combine(self, other):
        self.copies += 1

        if self.copies == 3:
            self.level = 2
            bonus_unit = True
        elif self.copies == 6:
            self.level = 3
            bonus_unit = True
        else:
            bonus_unit = False

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

        return bonus_unit


class Food:
    def __init__(self, food_data):
        self.food_data = food_data


class BattlePet:
    def __init__(self, pet):
        self.attack = pet.total_attack()
        self.bonus_attack = 0
        self.health = pet.total_health()
        self.bonus_health = 0
        self.data = pet.data
        self.food = pet.food
    
    def total_attack(self):
        return self.attack + self.bonus_attack
    
    def total_health(self):
        return self.health + self.bonus_health
    
    def handle_event(self, event, source, friends, enemies, **kwargs):
        self.data.handle_event(self, event, source, friends, enemies, **kwargs)
        if self.food is not None:
            self.food.handle_event(self, event, source, friends, enemies, **kwargs)
        
    def __repr__(self):
        return f"{self.data.__class__.__name__}({self.total_attack()}, {self.total_health()})"



class Player:
    def __init__(self, health):
        self.pets = [None] * 5
        self.shop = []
        self.money = 0
        self.health = health

    def get_pets_for_battle(self):
        return [BattlePet(pet) for pet in self.pets if pet is not None]

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

    def add_bonus_unit(self, round):
        tier = current_tier(round)
        next_tier = min(6, tier + 1)

        new_pet = random.choice(pets.PACK1_PETS[next_tier])
        self.shop.append(Buyable(new_pet))  # FIXME this should be before food


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
    DRAW = 3


class Game:
    def __init__(self, verbose=False):
        self.verbose = verbose

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
        if self.round > 30:
            self.result = GameResult.DRAW

    def start_round(self):
        for player in self.players:
            player.refresh_shop(self.round)
            player.money = 10

    def finish_round(self):
        battle_result = resolve_battle(self.p1, self.p2)
        if self.verbose:
            print(self.round, self.p1.health, self.p2.health, battle_result)
        if battle_result == BattleResult.WIN:
            lose_round(self.p2, self.round)
        elif battle_result == BattleResult.LOSS:
            lose_round(self.p1, self.round)

    def current_player(self):
        return self.players[self.current_player_index]

    def step(self, action):
        if self.verbose:
            print("player", self.current_player_index, "plays", action)
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


def handle_event(event, source, friends, enemies, **kwargs):
    source.handle_event(event, source, friends, enemies, **kwargs)
    for pet in friends:
        pet.handle_event(event, source, friends, enemies, **kwargs)


def resolve_battle(p1, p2, verbose=False):
    p1_pets = p1.get_pets_for_battle()
    p2_pets = p2.get_pets_for_battle()
    while p1_pets and p2_pets:
        if verbose:
            print('p1:', p1_pets)
            print('p2:', p2_pets)
        p1_pets[-1].bonus_health -= p2_pets[-1].total_attack()
        p2_pets[-1].bonus_health -= p1_pets[-1].total_attack()
        if p1_pets[-1].total_health() <= 0:
            source = p1_pets.pop()
            handle_event(Event.FAINT, source, p1_pets, p2_pets, index=len(p1_pets) - 1)
        if p2_pets[-1].total_health() <= 0:
            source = p2_pets.pop()
            handle_event(Event.FAINT, source,  p1_pets, p2_pets, index=len(p1_pets) - 1)

    if p1_pets:
        return BattleResult.WIN
    elif p2_pets:
        return BattleResult.LOSS
    else:
        return BattleResult.DRAW
