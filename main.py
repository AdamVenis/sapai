import random

from game import *
from common import *

ALL_ACTIONS = (
    [EndTurn(), Roll()]
    + [Buy(i, j) for i in range(MAX_SHOP_SIZE) for j in range(MAX_PETS)]
    + [Reposition(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
    + [Sell(i) for i in range(MAX_PETS)]
    + [Combine(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
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

class Env:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.reset(**kwargs)

    def reset(self, **kwargs):
        self.game = Game(**kwargs)


def winrate(env, agents, num_episodes):
    num_p1_wins = 0
    for _ in range(num_episodes):
        env.reset()
        result = play_game(env, agents)
        if result == GameResult.P1_WIN:
            num_p1_wins += 1

    return num_p1_wins / num_episodes


if __name__ == "__main__":
    env = Env(verbose=False)
    # game = Game()
    # game.p1.pets = [Pet(pets.Ant()), Pet(pets.Cricket()), Pet(pets.Horse())]
    # game.p2.pets = [Pet(pets.Horse()), Pet(pets.Cricket())]
    print(winrate(env, [BuyAgent(), RandomAgent()], num_episodes=100))
    print(winrate(env, [RandomAgent(), EndTurnAgent()], num_episodes=100))
