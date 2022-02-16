import collections
import random

from game import *
from common import *

ALL_ACTIONS = (
    [EndTurn(), Roll()]
    + [Buy(i, j) for i in range(MAX_SHOP_SIZE) for j in range(MAX_PETS)]
    + [Reposition(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
    + [Sell(i) for i in range(MAX_PETS)]
    + [Combine(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
    + [ToggleFreeze(i) for i in range(MAX_SHOP_SIZE)]
)
# CONSIDER: a prior that decreases the probability of doing endturn, reposition, or sell


def play_game(env, agents):
    game = env.game
    while game.result == GameResult.UNFINISHED:
        agent = agents[game.current_player_index]
        action = agent.get_action(game)
        game.step(action)
    return game.result


class BuyAgent:
    def get_action(self, game):
        for i in range(MAX_SHOP_SIZE):
            for j in range(MAX_PETS):
                buy = Buy(i, j)
                if buy.valid(game.current_player(), game):
                    return buy

        return EndTurn()


class BuyStrongestAgent:
    def get_action(self, game):
        strongest_buy = None
        strongest_pet_data = None

        player = game.current_player()
        for i in range(MAX_SHOP_SIZE):
            for j in range(MAX_PETS):
                buy = Buy(i, j)
                if buy.valid(player, game) and isinstance(player.shop[i].data, PetData):
                    pet_data = player.shop[i].data
                    if (
                        strongest_pet_data is None
                        or pet_data.attack + pet_data.health
                        > strongest_pet_data.attack + strongest_pet_data.health
                    ):
                        strongest_pet_data = pet_data
                        strongest_buy = buy

        return EndTurn() if strongest_buy is None else strongest_buy


class EndTurnAgent:
    def get_action(self, game):
        return EndTurn()


class RandomAgent:
    def get_action(self, game):
        valid_actions = [
            action
            for action in ALL_ACTIONS
            if action.valid(game.current_player(), game)
        ]
        return random.choice(valid_actions)


class HeuristicAgent:
    def get_action(self, game):
        # buy strongest pet, otherwise
        # sell and rebuy stronger
        # buy food if target has no food (FIXME), otherwise
        # roll (FIXME)

        strongest_buy = None
        strongest_pet_data = None

        player = game.current_player()
        for i in range(MAX_SHOP_SIZE):
            for j in range(MAX_PETS):
                buy = Buy(i, j)
                if buy.valid(player, game) and isinstance(player.shop[i].data, PetData):
                    pet_data = player.shop[i].data
                    if (
                        strongest_pet_data is None
                        or pet_data.attack + pet_data.health
                        > strongest_pet_data.attack + strongest_pet_data.health
                    ):
                        strongest_pet_data = pet_data
                        strongest_buy = buy

        if strongest_buy is not None:
            return strongest_buy

        if player.money >= 2:
            weakest_owned_pet = None
            weakest_owned_pet_index = None
            for i, pet in enumerate(player.pets):
                if (
                    weakest_owned_pet is None
                    or pet.total_attack() + pet.total_health()
                    < weakest_owned_pet.total_attack()
                    + weakest_owned_pet.total_health()
                ):
                    weakest_owned_pet = pet
                    weakest_owned_pet_index = i

            strongest_buyable_pet = None
            for i, pet in enumerate(player.shop):
                if not isinstance(pet.data, PetData):
                    continue
                if (
                    strongest_buyable_pet is None
                    or pet.data.attack + pet.data.health
                    > strongest_buyable_pet.data.attack
                    + strongest_buyable_pet.data.health
                ):
                    strongest_buyable_pet = pet

            if (
                weakest_owned_pet.total_attack() + weakest_owned_pet.total_health()
                < strongest_buyable_pet.data.attack + strongest_buyable_pet.data.health
            ):
                return Sell(weakest_owned_pet_index)

        return EndTurn()


class Env:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.reset()

    def reset(self):
        self.game = Game(**self.kwargs)


def winrate(env, agents, num_episodes):
    results = collections.defaultdict(int)
    for _ in range(num_episodes):
        env.reset()
        result = play_game(env, agents)
        results[result] += 1

    return {k: v / num_episodes for k, v in results.items()}


def evaluate_winrates(env, num_episodes):
    print(winrate(env, [HeuristicAgent(), BuyStrongestAgent()], num_episodes))  # ~54%
    print(winrate(env, [BuyStrongestAgent(), BuyAgent()], num_episodes))  # ~52%
    print(winrate(env, [BuyAgent(), RandomAgent()], num_episodes))  # 99%
    print(winrate(env, [RandomAgent(), EndTurnAgent()], num_episodes))  # 99%


if __name__ == "__main__":
    env = Env()

    evaluate_winrates(env, num_episodes=100)
