from dataclasses import dataclass
import enum
import copy
import random

import pets

def empty_effect():
    pass

# possible actions:
# end turn
# buy [pet/food] - requires index * target
# reposition - requires from_index * to_index
# sell pet - requires index
# combine pet - requires index * target

class Action:
    def act():
        pass


@dataclass
class EndTurn:
    def valid():
        return True


@dataclass
class Buy:
    def __init__(self, source_index, target_index):
        self.source_index = source_index
        self.target_index = target_index
    
    def validate(self, game):
        player = game.players[game.current_player_index]
        # invalid source
        # invalid target
        # not enough money
        return True # FIXME

    def act(self, game):
        player = game.players[game.current_player_index]
        player.money -= 3 # FIXME
        purchased = player.shop[source_index]
        if isinstance(purchased.data, PetData):
            player.pets[target_index] = Pet(purchased.data)
            # add a pet in target location FIXME
        else:
            # attach food to pet in target location FIXME
            pass


@dataclass
class Reposition:
    def __init__(self, source_index, target_index):
        self.source_index = source_index
        self.target_index = target_index
    
@dataclass
class Sell:
    def __init__(self, index):
        self.index = index

@dataclass
class Combine:
    def __init__(self, source_index, target_index):
        self.source_index = source_index
        self.target_index = target_index
    
# add some pets here (there are 80 lol)
class Pet:
    def __init__(self, pet_data):
        self.attack = pet_data.attack
        self.health = pet_data.health
        self.tier = pet_data.tier
        self.food = None
        self.effect = empty_effect


class Food:
    def __init__(self, food_data):
        self.food_data = food_data


class Player:
    def __init__(self, health):
        self.pets = []
        self.shop = []
        self.money = 0
        self.health = health
    
    def get_pets_for_battle(self):
        return [copy.copy(pet) for pet in self.pets]


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
    
    def check_result(self):
        if self.p2.health <= 0:
            self.result = GameResult.P1_WIN
        if self.p1.health <= 0:
            self.result = GameResult.P2_WIN

    def run(self):
        while self.result == GameResult.UNFINISHED:
            self.round += 1
            for player in self.players:
                refresh_shop(player, self.round)
                player.money = 10
            
            # <play the actual game> FIXME

            battle_result = resolve_battle(self.p1, self.p2)
            # print(self.round, self.p1.health, self.p2.health, battle_result)
            if battle_result == BattleResult.WIN:
                lose_round(self.p2, self.round)
            elif battle_result == BattleResult.LOSS:
                lose_round(self.p1, self.round)
        
            self.check_result()
        return self.result
    
    # def step(self, action):
    #     if action 


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


def refresh_shop(player, round):
    # seems to be uniform with replacement among all available pets
    new_pet_shop = []
    new_food_shop = []
    for buyable in player.shop:
        if buyable.frozen:
            if isinstance(buyable.data, PetData):
                new_pet_shop.append(buyable)
            else:
                new_food_shop.append(buyable)

    tier = current_tier(round)

    max_pets = 3 # FIXME
    max_food = 2 # FIXME

    while len(new_pet_shop) < max_pets:
        new_pet = random.choice(pets.PACK1_AVAILABLE_PETS[tier])
        new_pet_shop.append(Buyable(new_pet))

    while len(new_food_shop) < max_food:
        new_food = random.choice(pets.PACK1_AVAILABLE_FOOD[tier])
        new_food_shop.append(Buyable(new_food))

    player.shop = new_pet_shop + new_food_shop


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


if __name__ == '__main__':
    game = Game()
    game.p1.pets = [Pet(pets.Ant()), Pet(pets.Cricket()), Pet(pets.Horse())]
    game.p2.pets = [Pet(pets.Horse()), Pet(pets.Cricket())]
    print(game.run())


