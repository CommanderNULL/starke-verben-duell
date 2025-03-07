import unittest
from app import Game, GameState, db, app
import shortuuid

class TestGameAdvanced(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.game = Game()
        # Убедимся, что используем режим игры с ботом для тестов
        self.game.game_type = "bot"
        
    def tearDown(self):
        db.session.remove()
        self.app_context.pop()
        
    def test_bot_move(self):
        """Проверка хода бота - успешный ход"""
        # Установим текущий ход для бота
        self.game.current_turn = "opponent"
        
        # Создаем карту, которая находится в верхней части стопки сброса
        top_card = self.game.discard_pile[-1]
        
        # Создаем карту, которую бот может сыграть (с тем же глаголом)
        bot_card = (top_card[0], top_card[1], (top_card[2] + 1) % 4, "test")
        # Добавим еще одну карту, чтобы после хода у бота оставались карты
        extra_card = ("Präsens", "helfen", 1, "помогать")
        self.game.players["opponent"] = [bot_card, extra_card]
        
        # Запускаем ход бота
        success, message = self.game.bot_move()
        
        # Проверяем, что ход был успешным
        self.assertTrue(success)
        # Проверяем, что карта бота была перемещена в стопку сброса
        self.assertIn(bot_card, self.game.discard_pile)
        # Проверяем, что у бота осталась одна карта
        self.assertEqual(len(self.game.players["opponent"]), 1)
        # Проверяем, что ход передан игроку
        self.assertEqual(self.game.current_turn, "player")

    def test_bot_win_condition(self):
        """Проверка победы бота - когда бот использует последнюю карту"""
        # Установим текущий ход для бота
        self.game.current_turn = "opponent"
        
        # Создаем карту, которая находится в верхней части стопки сброса
        top_card = self.game.discard_pile[-1]
        
        # Создаем карту, которую бот может сыграть (с тем же глаголом)
        bot_card = (top_card[0], top_card[1], (top_card[2] + 1) % 4, "test")
        # Добавляем только одну карту
        self.game.players["opponent"] = [bot_card]
        
        # Запускаем ход бота
        success, message = self.game.bot_move()
        
        # Проверяем, что ход был успешным
        self.assertTrue(success)
        # Проверяем, что карта бота была перемещена в стопку сброса
        self.assertIn(bot_card, self.game.discard_pile)
        # Проверяем, что у бота не осталось карт
        self.assertEqual(len(self.game.players["opponent"]), 0)
        # Проверяем, что игра завершена
        self.assertEqual(self.game.current_turn, "over")
        # Проверяем сообщение о победе
        self.assertTrue("выиграл" in message)
        
    def test_bot_move_no_valid_move(self):
        """Проверка хода бота - когда нет валидного хода"""
        # Установим текущий ход для бота
        self.game.current_turn = "opponent"
        
        # Создаем карту, которая находится в верхней части стопки сброса
        top_card = self.game.discard_pile[-1]
        
        # Создаем карту, которую бот НЕ может сыграть (с другим глаголом и другим индексом)
        different_verb = "kommen" if top_card[1] != "kommen" else "gehen"
        bot_card = ("Futur", different_verb, (top_card[2] + 1) % 4, "test")
        self.game.players["opponent"] = [bot_card]
        
        # Запоминаем начальное количество карт у бота
        initial_cards = len(self.game.players["opponent"])
        
        # Запускаем ход бота
        success, message = self.game.bot_move()
        
        # Проверяем, что ход был успешным (бот взял карту)
        self.assertTrue(success)
        # Проверяем, что у бота стало на 1 карту больше
        self.assertEqual(len(self.game.players["opponent"]), initial_cards + 1)
        
    def test_get_state(self):
        """Проверка получения состояния игры"""
        # Подготавливаем данные для состояния
        self.game.players["player"] = [("Präsens", "gehen", 0, "идти")]
        self.game.players["opponent"] = [("Präsens", "kommen", 1, "приходить")]
        self.game.discard_pile = [("Futur", "fahren", 2, "ехать")]
        self.game.current_turn = "player"
        
        # Получаем состояние
        state = self.game.get_state()
        
        # Проверяем ключи в состоянии
        self.assertIn("player_cards", state)
        self.assertIn("opponent_cards_count", state)
        self.assertIn("discard_pile", state)
        self.assertIn("current_turn", state)
        
        # Проверяем значения
        self.assertEqual(state["player_cards"], self.game.players["player"])
        self.assertEqual(state["opponent_cards_count"], len(self.game.players["opponent"]))
        self.assertEqual(state["discard_pile"], self.game.discard_pile[-1])
        self.assertEqual(state["current_turn"], self.game.current_turn)
        
    def test_check_if_playable(self):
        """Проверка метода проверки возможности хода"""
        # Создаем карту, которая находится в верхней части стопки сброса
        top_card = self.game.discard_pile[-1]
        
        # Создаем карту, которую можно сыграть (с тем же глаголом)
        playable_card = (top_card[0], top_card[1], (top_card[2] + 1) % 4, "test")
        self.game.players["player"] = [playable_card]
        
        # Проверяем, что есть возможность сделать ход
        self.assertTrue(self.game.check_if_playable())
        
        # Теперь создаем карту, которую нельзя сыграть
        different_verb = "kommen" if top_card[1] != "kommen" else "gehen"
        unplayable_card = ("Futur", different_verb, (top_card[2] + 1) % 4, "test")
        self.game.players["player"] = [unplayable_card]
        
        # Проверяем, что нет возможности сделать ход
        self.assertFalse(self.game.check_if_playable())
        
    def test_save_state(self):
        """Проверка сохранения состояния игры в базу данных"""
        # Инициализируем игру с предсказуемым состоянием
        game = Game()
        game.players["player"] = [("Präsens", "gehen", 0, "идти")]
        game.players["opponent"] = [("Präsens", "kommen", 1, "приходить")]
        game.discard_pile = [("Futur", "fahren", 2, "ехать")]
        game.current_turn = "player"
        
        # Создаем уникальный идентификатор для тестовой игры
        test_game_id = "test_" + shortuuid.uuid()[:6]
        
        try:
            # Сохраняем состояние в базу данных
            game.save_state(test_game_id, "TestPlayer", "TestOpponent", "multiplayer")
            
            # Проверяем, что запись была создана
            game_state = GameState.query.get(test_game_id)
            
            # Проверяем, что данные правильно сохранены
            self.assertIsNotNone(game_state)
            self.assertEqual(game_state.player_name, "TestPlayer")
            self.assertEqual(game_state.opponent_name, "TestOpponent")
            self.assertEqual(game_state.game_type, "multiplayer")
            self.assertEqual(game_state.current_turn, "player")
            
        except Exception as e:
            self.fail(f"Тест сохранения состояния не прошел: {str(e)}")
        finally:
            # Удаляем тестовую запись из базы данных
            game_state = GameState.query.get(test_game_id)
            if game_state:
                db.session.delete(game_state)
                db.session.commit()

if __name__ == '__main__':
    unittest.main() 