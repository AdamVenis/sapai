import random

from game import *
from common import *

# possible actions:
# end turn
# buy [pet/food] - requires index * target
# reposition - requires from_index * to_index
# sell pet - requires index
# combine pet - requires index * target
# roll
ALL_ACTIONS = (
    [EndTurn(), Roll()]
    + [Buy(i, j) for i in range(MAX_SHOP_SIZE) for j in range(MAX_PETS)]
    + [Reposition(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
    + [Sell(i) for i in range(MAX_PETS)]
    + [Combine(i, j) for i in range(MAX_PETS) for j in range(MAX_PETS)]
)
# CONSIDER: a prior that decreases the probability of doing endturn, reposition, or sell


def play_game(game, agents):
    while game.result == GameResult.UNFINISHED:
        agent = agents[game.current_player_index]
        action = agent.get_action(game)
        game.step(action)
    return game.result


class BuyOnceAgent:
    def __init__(self):
        self.already_bought = False

    def get_action(self, game):
        if not self.already_bought:
            self.already_bought = True
            return Buy(0, 0)
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


def winrate(agents, num_episodes):
    num_p1_wins = 0
    for _ in range(num_episodes):
        result = play_game(Game(), agents)
        if result == GameResult.P1_WIN:
            num_p1_wins += 1

    return num_p1_wins / num_episodes


if __name__ == "__main__":
    # game = Game()
    # game.p1.pets = [Pet(pets.Ant()), Pet(pets.Cricket()), Pet(pets.Horse())]
    # game.p2.pets = [Pet(pets.Horse()), Pet(pets.Cricket())]
    # print(play_game(Game(), [BuyOnceAgent(), EndTurnAgent()]))
    # print(play_game(Game(), [EndTurnAgent(), BuyOnceAgent()]))
    print(winrate([RandomAgent(), RandomAgent()], num_episodes=100))
