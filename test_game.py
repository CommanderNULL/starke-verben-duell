import unittest
from app import Game, Card

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        
    def test_initial_state(self):
        """Проверка начального состояния игры"""
        self.assertEqual(len(self.game.player_cards), 10)
        self.assertEqual(len(self.game.bot_cards), 10)
        self.assertEqual(len(self.game.table_cards), 1)
        
    def test_valid_move(self):
        """Проверка валидного хода"""
        # Создаем карточку, которая совпадает с верхней на столе
        top_card = self.game.table_cards[-1]
        matching_card = Card(top_card.verb, top_card.form)
        
        # Проверяем, что ход валидный
        self.assertTrue(self.game.is_valid_move(matching_card))
        
    def test_invalid_move(self):
        """Проверка невалидного хода"""
        # Создаем карточку, которая не совпадает с верхней на столе
        top_card = self.game.table_cards[-1]
        different_verb = "kommen" if top_card.verb != "kommen" else "gehen"
        invalid_card = Card(different_verb, "Präsens")
        
        # Проверяем, что ход невалидный
        self.assertFalse(self.game.is_valid_move(invalid_card))
        
    def test_draw_card(self):
        """Проверка взятия новой карточки"""
        initial_cards = len(self.game.player_cards)
        self.game.draw_card()
        self.assertEqual(len(self.game.player_cards), initial_cards + 1)
        
    def test_win_condition(self):
        """Проверка условия победы"""
        # Очищаем карточки игрока
        self.game.player_cards = []
        self.assertTrue(self.game.check_win_condition())
        
    def test_three_turns_rule(self):
        """Проверка правила трех ходов"""
        # Симулируем три хода без возможности сходить
        self.game.consecutive_invalid_moves = 3
        initial_table_cards = len(self.game.table_cards)
        self.game.handle_three_turns_rule()
        self.assertEqual(len(self.game.table_cards), initial_table_cards)

if __name__ == '__main__':
    unittest.main() 