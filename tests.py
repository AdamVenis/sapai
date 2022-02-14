import unittest

from game import *
from common import *


class TestEverything(unittest.TestCase):
    def test_ant(self):
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Beaver()), Pet(pets.Ant())]
        game.p2.pets[:2] = [Pet(pets.Horse()), Pet(pets.Horse())]
        assert game.resolve_battle() == BattleResult.P1_WIN

    def test_duck(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Duck())
        game.p1.shop[0] = Buyable(pets.Pig())
        game.step(Sell(0))
        assert game.p1.shop[0].total_health() == 2

    @unittest.skip("")
    def test_hedgehog_combine(self):
        # 1) faint a hedgehog outside of battle with a sleeping pill
        # 2) damage two level 1 fish from 2/3 to 2/1 each
        # 3) combine them. => 3/4? or a 3/2?
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Fish()), Pet(pets.Fish()), Pet(pets.Hedgehog())]
        game.p1.shop[-1] = pets.SleepingPill()
        game.step(Buy(len(game.p1.shop) - 1, 2))
        game.step(Combine(1, 0))
        assert game.p1.pets[0].total_health() == 4

    @unittest.skip("")
    def test_dolphin_hedgehog(self):
        # assume attack order is dolphin -> croc -> hedgehog, but dolphin kills hedgehog.
        # does hedgehog faint effect go on the top of the stack, pre-empting the croc?
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Crocodile()), Pet(pets.Mosquito())]
        game.p1.shop[:2] = [Buyable(pets.Hedgehog()), Buyable(pets.Horse())]
        assert game.resolve_battle() == BattleResult.P1_WIN

    def test_fish(self):
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Beaver()), Pet(pets.Fish())]
        game.p1.shop[:2] = [Buyable(pets.Fish()), Buyable(pets.Fish())]
        game.step(Buy(0, 1))
        game.step(Buy(1, 1))
        assert str(game.p1.pets) == "[Beaver(3, 3), Fish(5, 6), None, None, None]"

    def test_horse(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Horse())
        game.p2.pets[0] = Pet(pets.Fish())
        game.p1.shop[0] = Buyable(pets.Fish())
        game.step(Buy(0, 1))
        game.step(Sell(0))
        assert game.resolve_battle() == BattleResult.P1_WIN

    def test_otter(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Horse())
        game.p1.shop[0] = Buyable(pets.Otter())
        game.step(Buy(0, 1))
        assert str(game.p1.pets) == "[Horse(3, 2), Otter(2, 2), None, None, None]"

    def test_pig(self):
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Pig())]
        game.step(Sell(0))
        assert game.p1.money == 12

    def test_beaver(self):
        game = Game()
        game.p1.pets[:2] = [Pet(pets.Beaver()), Pet(pets.Pig())]
        game.step(Sell(0))
        assert game.p1.pets[1].total_health() == 2

    def test_mosquito(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Mosquito())
        game.p2.pets[0] = Pet(pets.Fish())
        assert game.resolve_battle() == BattleResult.DRAW

    def test_cricket(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Cricket())
        game.p2.pets[0] = Pet(pets.Pig())
        assert game.resolve_battle() == BattleResult.P1_WIN

    def test_apple(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Beaver())
        game.p2.pets[0] = Pet(pets.Beaver())
        game.p1.shop[-1] = Buyable(pets.Apple())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        assert game.resolve_battle() == BattleResult.P1_WIN

    def test_honey(self):
        game = Game()
        game.p1.pets[0] = Pet(pets.Pig())
        game.p2.pets[0] = Pet(pets.Pig())
        game.p1.shop[-1] = Buyable(pets.Honey())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        assert game.resolve_battle() == BattleResult.P1_WIN

if __name__ == "__main__":
    unittest.main()
