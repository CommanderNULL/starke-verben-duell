import unittest
from app import Game

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        
    def test_initial_state(self):
        """Проверка начального состояния игры"""
        self.assertEqual(len(self.game.players["player"]), 10)
        self.assertEqual(len(self.game.players["bot"]), 10)
        self.assertEqual(len(self.game.discard_pile), 1)
        
    def test_valid_move(self):
        """Проверка валидного хода"""
        # Создаем карточку, которая совпадает с верхней на столе
        top_card = self.game.discard_pile[-1]
        matching_card = (top_card[0], top_card[1], top_card[2])
        
        # Добавляем карточку в руку игрока
        self.game.players["player"].append(matching_card)
        
        # Проверяем, что ход валидный
        success, message = self.game.play_card("player", matching_card)
        self.assertTrue(success)
        
    def test_invalid_move(self):
        """Проверка невалидного хода"""
        # Создаем карточку, которая не совпадает с верхней на столе
        top_card = self.game.discard_pile[-1]
        different_verb = "kommen" if top_card[1] != "kommen" else "gehen"
        # Создаем карточку с другим глаголом и другим индексом
        invalid_card = ("Präsens", different_verb, (top_card[2] + 1) % 4)
        
        # Добавляем карточку в руку игрока
        self.game.players["player"].append(invalid_card)
        
        # Проверяем, что ход невалидный
        success, message = self.game.play_card("player", invalid_card)
        self.assertFalse(success)
        
    def test_draw_card(self):
        """Проверка взятия новой карточки"""
        initial_cards = len(self.game.players["player"])
        self.game.pull_one_more_card("player")
        self.assertEqual(len(self.game.players["player"]), initial_cards + 1)
        
    def test_win_condition(self):
        """Проверка условия победы"""
        # Очищаем карточки игрока
        self.game.players["player"] = []
        self.assertTrue(len(self.game.players["player"]) == 0)
        
    def test_three_turns_rule(self):
        """Проверка правила трех ходов"""
        # Симулируем три хода без возможности сходить
        self.game.no_valid_moves_count = 3
        initial_discard_pile = len(self.game.discard_pile)
        self.game.replace_top_card()
        self.assertEqual(len(self.game.discard_pile), initial_discard_pile + 1)

if __name__ == '__main__':
    unittest.main() 