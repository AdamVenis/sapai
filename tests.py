import unittest

from game import *
from common import *


class TestEverything(unittest.TestCase):
    def test_ant(self):
        game = Game()
        game.p1.pets = [Pet(pets.Beaver()), Pet(pets.Ant())]
        game.p2.pets = [Pet(pets.Horse()), Pet(pets.Horse())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_duck(self):
        game = Game()
        game.p1.pets = [Pet(pets.Duck())]
        game.p1.shop = [Buyable(pets.Pig())]
        game.step(Sell(0))
        self.assertEqual(game.p1.shop[0].total_health(), 2)

    @unittest.skip("")
    def test_hedgehog_combine(self):
        # 1) faint a hedgehog outside of battle with a sleeping pill
        # 2) damage two level 1 fish from 2/3 to 2/1 each
        # 3) combine them. => 3/4? or a 3/2?
        game = Game()
        game.p1.pets = [Pet(pets.Fish()), Pet(pets.Fish()), Pet(pets.Hedgehog())]
        game.p1.shop[-1] = pets.SleepingPill()
        game.step(Buy(len(game.p1.shop) - 1, 2))
        game.step(Combine(1, 0))
        self.assertEqual(game.p1.pets[0].total_health(), 4)

    @unittest.skip("")
    def test_dolphin_hedgehog(self):
        # assume attack order is dolphin -> croc -> hedgehog, but dolphin kills hedgehog.
        # does hedgehog faint effect go on the top of the stack, pre-empting the croc?
        game = Game()
        game.p1.pets = [Pet(pets.Crocodile()), Pet(pets.Mosquito())]
        game.p1.shop[:2] = [Buyable(pets.Hedgehog()), Buyable(pets.Horse())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_fish(self):
        game = Game()
        game.p1.pets = [Pet(pets.Beaver()), Pet(pets.Fish())]
        game.p1.shop[:2] = [Buyable(pets.Fish()), Buyable(pets.Fish())]
        game.step(Buy(0, 1))
        game.step(Buy(1, 1))
        self.assertEqual(str(game.p1.pets), "[Beaver(3, 3), Fish(5, 6)]")

    def test_horse(self):
        game = Game()
        game.p1.pets = [Pet(pets.Horse())]
        game.p2.pets = [Pet(pets.Fish())]
        game.p1.shop[0] = Buyable(pets.Fish())
        game.step(Buy(0, 1))
        game.step(Sell(0))
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_otter(self):
        game = Game()
        game.p1.pets = [Pet(pets.Horse())]
        game.p1.shop[0] = Buyable(pets.Otter())
        game.step(Buy(0, 1))
        self.assertEqual(str(game.p1.pets), "[Horse(3, 2), Otter(2, 2)]")

    def test_pig(self):
        game = Game()
        game.p1.pets = [Pet(pets.Pig())]
        game.step(Sell(0))
        self.assertEqual(game.p1.money, 12)

    def test_beaver(self):
        game = Game()
        game.p1.pets = [Pet(pets.Beaver()), Pet(pets.Pig())]
        game.step(Sell(0))
        self.assertEqual(game.p1.pets[0].total_health(), 2)

    def test_mosquito(self):
        game = Game()
        game.p1.pets = [Pet(pets.Mosquito())]
        game.p2.pets = [Pet(pets.Fish())]
        self.assertEqual(game.resolve_battle(), BattleResult.DRAW)

    def test_cricket(self):
        game = Game()
        game.p1.pets = [Pet(pets.Cricket())]
        game.p2.pets = [Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_apple(self):
        game = Game()
        game.p1.pets = [Pet(pets.Beaver())]
        game.p2.pets = [Pet(pets.Beaver())]
        game.p1.shop[-1] = Buyable(pets.Apple())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_honey(self):
        game = Game()
        game.p1.pets = [Pet(pets.Pig())]
        game.p2.pets = [Pet(pets.Pig())]
        game.p1.shop[-1] = Buyable(pets.Honey())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_swan(self):
        game = Game()
        game.p1.pets = [Pet(pets.Swan())]
        game.step(EndTurn())
        game.step(EndTurn())
        self.assertEqual(game.p1.money, 11)

    def test_crab(self):
        game = Game()
        game.p1.pets = [Pet(pets.Peacock())]
        game.p1.shop = [Buyable(pets.Crab())]
        game.step(Buy(0, 1))
        self.assertEqual(game.p1.pets[1].total_health(), 5)

    def test_shrimp(self):
        game = Game()
        game.p1.pets = [Pet(pets.Shrimp()), Pet(pets.Pig())]
        game.step(Sell(1))
        self.assertEqual(game.p1.pets[0].total_health(), 4)

    def test_dodo(self):
        game = Game()
        game.p1.pets = [Pet(pets.Dodo()), Pet(pets.Fish())]
        game.p2.pets = [Pet(pets.Fish()), Pet(pets.Fish())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_spider(self):
        game = Game()
        game.p1.pets = [Pet(pets.Spider())]
        game.p2.pets = [Pet(pets.Beaver())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_elephant(self):
        game = Game()
        game.p1.pets = [Pet(pets.Pig()), Pet(pets.Elephant())]
        game.p2.pets = [Pet(pets.Pig()), Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.DRAW)

    def test_rat(self):
        game = Game()
        game.p1.pets = [Pet(pets.Rat())]
        game.p2.pets = [Pet(pets.Pig()), Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.P2_WIN)

    def test_hedgehog(self):
        game = Game()
        game.p1.pets = [Pet(pets.Hedgehog())]
        game.p2.pets = [Pet(pets.Pig()), Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.DRAW)

    def test_peacock(self):
        game = Game()
        game.p1.pets = [Pet(pets.Peacock())]
        game.p2.pets = [Pet(pets.Fish()), Pet(pets.Fish())]
        self.assertEqual(game.resolve_battle(), BattleResult.DRAW)

    def test_meat_bone(self):
        game = Game()
        game.p1.pets = [Pet(pets.Fish())]
        game.p2.pets = [Pet(pets.Fish())]
        game.p1.shop[-1] = Buyable(pets.MeatBone())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_sleeping_pill(self):
        game = Game()
        game.p1.pets = [Pet(pets.Cricket())]
        game.p2.pets = [Pet(pets.Fish())]
        game.p1.shop[-1] = Buyable(pets.SleepingPill())
        game.step(Buy(len(game.p1.shop) - 1, 0))
        self.assertEqual(str(game.p1.pets), "[ZombieCricket(1, 1)]")

    def test_turtle(self):
        game = Game()
        game.p1.pets = [Pet(pets.Pig()), Pet(pets.Turtle())]
        game.p2.pets = [Pet(pets.Pig()), Pet(pets.Pig()), Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.DRAW)

    def test_giraffe(self):
        game = Game()
        game.p1.pets = [Pet(pets.Giraffe()), Pet(pets.Beaver())]
        game.p2.pets = [Pet(pets.Elephant()), Pet(pets.Swan()), Pet(pets.Swan())]
        game.step(EndTurn())
        game.step(EndTurn())
        self.assertEqual(game.p1.health, 10)
        assert game.p2.health < 10

    def test_sheep(self):
        game = Game()
        game.p1.pets = [Pet(pets.Sheep())]
        game.p2.pets = [Pet(pets.Beaver()), Pet(pets.Beaver())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)

    def test_snail(self):
        game = Game()
        game.p1.pets = [Pet(pets.Beaver())]
        game.p2.pets = [Pet(pets.Fish())]
        game.step(EndTurn())
        game.step(EndTurn())
        game.p1.shop[0] = Buyable(pets.Snail())
        game.step(Buy(0, 1))
        self.assertEqual(game.p1.pets[0].total_attack(), 3)
        self.assertEqual(game.p1.pets[0].total_health(), 3)


    def test_honey_badger(self):
        game = Game()
        game.p1.pets = [Pet(pets.Badger())]
        game.p1.pets[0].food = pets.Honey()
        game.p2.pets = [Pet(pets.Pig()), Pet(pets.Pig()), Pet(pets.Pig())]
        self.assertEqual(game.resolve_battle(), BattleResult.P1_WIN)


if __name__ == "__main__":
    unittest.main()
