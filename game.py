from dataclasses import dataclass
import enum
import copy
import random

import pets
from common import *


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
        if self.source_index >= len(player.shop):
            return False
        if player.money < 3:  # FIXME - sometimes things are cheaper, like milk
            return False

        purchased = player.shop[self.source_index]
        if isinstance(purchased.data, PetData):
            if self.target_index >= len(player.pets):
                return True

            target_pet = player.pets[self.target_index]
            if target_pet.level == 3 or target_pet.data != purchased.data:
                return False
        else:
            if self.target_index >= len(player.pets):
                return False

        return True

    def act(self, player, game):
        player.money -= 3  # FIXME
        purchased = player.shop[self.source_index]
        if isinstance(purchased.data, PetData):
            new_pet = Pet(purchased.data)
            if self.target_index < len(player.pets):
                target_pet = player.pets[self.target_index]
                level_up = target_pet.combine(new_pet)
                if level_up:
                    target_pet.data.handle_event(
                        target_pet,
                        Event.LEVEL_UP,
                        source=target_pet,
                        friends=player.pets,
                    )
                    player.add_bonus_unit(game.round)
            else:
                player.pets.append(new_pet)
                target_pet = player.pets[-1]

            for pet in player.pets:
                pet.data.handle_event(
                    pet,
                    Event.BUY,
                    source=target_pet,
                    friends=player.pets,
                    lost_last_turn=player.lost_last_turn,
                )
                pet.data.handle_event(
                    pet,
                    Event.SUMMON,
                    source=target_pet,
                    friends=player.pets,
                    lost_last_turn=player.lost_last_turn,
                )

        elif isinstance(purchased.data, ConsumableFood):
            target_pet = player.pets[self.target_index]
            for pet in player.pets:
                pet.data.handle_event(
                    pet, Event.EAT, food=purchased.data, target=target_pet
                )
            purchased.data.consume(pet, friends=player.pets)

        elif isinstance(purchased.data, EquippableFood):
            target_pet = player.pets[self.target_index]
            for pet in player.pets:
                pet.data.handle_event(
                    pet, Event.EAT, food=purchased.data, target=target_pet
                )
            target_pet.food = purchased.data


@dataclass
class Reposition:
    source_index: int
    target_index: int

    def valid(self, player, game):
        return self.source_index < len(player.pets) and self.target_index < len(
            player.pets
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
        return self.index < len(player.pets)

    def act(self, player, game):
        sold_pet = player.pets[self.index]
        del player.pets[self.index]

        for pet in player.pets:
            pet.data.handle_event(pet, Event.SELL, source=sold_pet, friends=player.pets)
        sold_pet.data.handle_event(
            sold_pet, Event.SELL, source=sold_pet, friends=player.pets, player=player
        )
        player.money += sold_pet.level


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
        if self.source_index >= len(player.pets) or self.target_index >= len(
            player.pets
        ):
            return False

        pet1, pet2 = player.pets[self.source_index], player.pets[self.target_index]
        return pet1.data == pet2.data

    def act(self, player, game):
        target_pet = player.pets[self.target_index]
        level_up = target_pet.combine(player.pets[self.source_index])
        if level_up:
            player.add_bonus_unit(game.round)
        del player.pets[self.source_index]


@dataclass
class ToggleFreeze:
    index: int

    def valid(self, player, game):
        return 0 <= self.index < len(player.shop)

    def act(self, player, game):
        player.shop[self.index].frozen ^= True  # fanciest toggle in the west


class Food:
    def __init__(self, food_data):
        self.food_data = food_data


class Player:
    def __init__(self, health):
        self.pets = []
        self.shop = []
        self.money = 0
        self.health = health
        self.lost_last_turn = False

    def get_pets_for_battle(self):
        return [pet.to_battle_pet() for pet in self.pets]

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
        self.bonus_attack = 0
        self.bonus_health = 0
        self.data = pet_or_food_data
        self.frozen = False

    def total_attack(self):
        # FIXME - this doesn't make sense for food
        return self.data.attack + self.bonus_attack

    def total_health(self):
        return self.data.health + self.bonus_health

    def __repr__(self):
        if isinstance(self.data, PetData):
            return f"{self.data.__class__.__name__}({self.total_attack()}, {self.total_health()})"
        else:
            return self.data.__class__.__name__


class BattleResult(enum.Enum):
    P1_WIN = 1
    DRAW = 2
    P2_WIN = 3


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
            for pet in player.pets:
                pet.battle_attack = 0
                pet.battle_health = 0
                pet.data.handle_event(pet, Event.START_ROUND, source=pet, player=player)

    def finish_round(self):
        battle_result = self.resolve_battle()
        if self.verbose:
            print(self.round, self.p1.health, self.p2.health, battle_result)

        self.p1.lost_last_turn, self.p2.lost_last_turn = False, False
        if battle_result == BattleResult.P1_WIN:
            lose_round(self.p2, self.round)
        elif battle_result == BattleResult.P2_WIN:
            lose_round(self.p1, self.round)

    def resolve_battle(self):
        p1_pets = self.p1.get_pets_for_battle()
        p2_pets = self.p2.get_pets_for_battle()

        # FIXME go in decreasing order of attack
        for pet in p1_pets:
            pet.handle_event(Event.START_BATTLE, friends=p1_pets, enemies=p2_pets)

        for pet in p2_pets:
            pet.handle_event(Event.START_BATTLE, friends=p2_pets, enemies=p1_pets)

        while p1_pets and p2_pets:
            if self.verbose:
                print("p1:", p1_pets)
                print("p2:", p2_pets)

            for pet in p1_pets:
                pet.handle_event(Event.BEFORE_ATTACK, friends=p1_pets, enemies=p2_pets)
            for pet in p2_pets:
                pet.handle_event(Event.BEFORE_ATTACK, friends=p2_pets, enemies=p1_pets)

            if len(p1_pets) == 0 or len(p2_pets) == 0:
                break

            p1_damage = p1_pets[-1].total_attack()
            p2_damage = p2_pets[-1].total_attack()
            p1_pets[-1].take_damage(p2_damage)
            p2_pets[-1].take_damage(p1_damage)

            for pet in p1_pets:
                pet.handle_event(
                    Event.HURT,
                    damage=p2_damage,
                    source=p1_pets[-1],
                    friends=p1_pets,
                    enemies=p2_pets,
                )
            for pet in p2_pets:
                pet.handle_event(
                    Event.HURT,
                    damage=p1_damage,
                    source=p2_pets[-1],
                    friends=p2_pets,
                    enemies=p1_pets,
                )

            if len(p1_pets) == 0 or len(p2_pets) == 0:
                break

            for pet in p1_pets:
                pet.handle_event(
                    Event.AFTER_ATTACK,
                    source=p1_pets[-1],
                    target=p2_pets[-1],
                    friends=p1_pets,
                    enemies=p2_pets,
                )
            for pet in p2_pets:
                pet.handle_event(
                    Event.AFTER_ATTACK,
                    source=p2_pets[-1],
                    target=p1_pets[-1],
                    friends=p2_pets,
                    enemies=p1_pets,
                )

            if p1_pets and p1_pets[-1].total_health() <= 0:
                # FIXME - if meat kills, this will unintentionally double kill
                source = p1_pets.pop()
                index = len(p1_pets)
                source.handle_event(
                    Event.SELF_FAINT,
                    source=source,
                    index=index,
                    friends=p1_pets,
                    enemies=p2_pets,
                )
                for pet in p1_pets:
                    pet.handle_event(
                        Event.FRIEND_FAINT,
                        source=source,
                        index=index,
                        friends=p1_pets,
                        enemies=p2_pets,
                    )
            if p2_pets and p2_pets[-1].total_health() <= 0:
                source = p2_pets.pop()
                index = len(p2_pets)
                source.handle_event(
                    Event.SELF_FAINT,
                    source=source,
                    index=index,
                    friends=p2_pets,
                    enemies=p1_pets,
                )
                for pet in p2_pets:
                    pet.handle_event(
                        Event.FRIEND_FAINT,
                        source=source,
                        index=index,
                        friends=p2_pets,
                        enemies=p1_pets,
                    )

        if self.verbose:
            print("p1:", p1_pets)
            print("p2:", p2_pets)

        if p1_pets:
            return BattleResult.P1_WIN
        elif p2_pets:
            return BattleResult.P2_WIN
        else:
            return BattleResult.DRAW

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
                for player in self.players:
                    for pet in player.pets:
                        pet.handle_event(Event.END_TURN, friends=player.pets)

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
    player.lost_last_turn = True
