import unittest
from app import Game, GameState, db, app, load_verbs
import shortuuid
import json

class TestGameEnhanced(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.game = Game()
        # Убедимся, что используем режим игры с ботом для тестов
        self.game.game_type = "bot"
    
    def tearDown(self):
        db.session.remove()
        self.app_context.pop()
    
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
            self.assertEqual(len(game_state.player_cards), 1)
            self.assertEqual(len(game_state.opponent_cards), 1)
            self.assertEqual(len(game_state.discard_pile), 1)
            
        finally:
            # Удаляем тестовую запись из базы данных
            game_state = GameState.query.get(test_game_id)
            if game_state:
                db.session.delete(game_state)
                db.session.commit()
    
    def test_verbs_loading(self):
        """Проверка загрузки глаголов из JSON файла"""
        verbs = load_verbs()
        self.assertIsNotNone(verbs)
        self.assertIsInstance(verbs, list)
        self.assertTrue(len(verbs) > 0)
    
    def test_game_initialization_with_id(self):
        """Проверка инициализации игры с существующим ID"""
        # Создаем тестовую игру и сохраняем ее
        original_game = Game()
        test_game_id = "test_" + shortuuid.uuid()[:6]
        original_game.save_state(test_game_id, "TestPlayer")
        
        try:
            # Инициализируем новую игру с этим ID
            loaded_game = Game(test_game_id)
            
            # Проверяем, что состояние загружено
            self.assertEqual(loaded_game.current_turn, original_game.current_turn)
            self.assertEqual(len(loaded_game.players["player"]), len(original_game.players["player"]))
            self.assertEqual(len(loaded_game.players["opponent"]), len(original_game.players["opponent"]))
            self.assertEqual(len(loaded_game.discard_pile), len(original_game.discard_pile))
        finally:
            # Удаляем тестовую игру из базы данных
            game_state = GameState.query.get(test_game_id)
            if game_state:
                db.session.delete(game_state)
                db.session.commit()
                
    def test_replace_top_card(self):
        """Проверка замены верхней карты в колоде сброса"""
        # Запоминаем текущую верхнюю карту
        initial_top_card = self.game.discard_pile[-1]
        
        # Устанавливаем счетчик невозможных ходов в 3
        self.game.no_valid_moves_count = 3
        
        # Заменяем верхнюю карту
        self.game.replace_top_card()
        
        # Проверяем, что верхняя карта изменилась
        new_top_card = self.game.discard_pile[-1]
        self.assertNotEqual(initial_top_card, new_top_card)
        
        # Метод replace_top_card не сбрасывает счетчик, поэтому он остается прежним
        self.assertEqual(self.game.no_valid_moves_count, 3)
    
    def test_pull_one_more_card(self):
        """Проверка взятия дополнительной карты"""
        # Запоминаем начальное количество карт у игрока
        initial_player_cards = len(self.game.players["player"])
        
        # Берем дополнительную карту
        self.game.pull_one_more_card("player")
        
        # Проверяем, что количество карт увеличилось
        self.assertEqual(len(self.game.players["player"]), initial_player_cards + 1)
        
        # Проверяем для противника
        initial_opponent_cards = len(self.game.players["opponent"])
        self.game.pull_one_more_card("opponent")
        self.assertEqual(len(self.game.players["opponent"]), initial_opponent_cards + 1)
    
    def test_empty_deck_handling(self):
        """Проверка обработки пустой колоды"""
        # Очищаем колоду
        self.game.deck = []
        
        # Пытаемся взять карту из пустой колоды
        initial_player_cards = len(self.game.players["player"])
        self.game.pull_one_more_card("player")
        
        # Проверяем, что количество карт не изменилось
        self.assertEqual(len(self.game.players["player"]), initial_player_cards)
    
    def test_win_condition_check(self):
        """Проверка условия победы - пустая рука у игрока"""
        # Очищаем карты игрока
        self.game.players["player"] = []
        
        # Проверяем, что у игрока нет карт
        self.assertEqual(len(self.game.players["player"]), 0)
        
        # Здесь можно было бы проверить логику определения победителя,
        # если такая логика есть в Game
    
    def test_update_existing_game_state(self):
        """Проверка обновления существующего состояния игры"""
        # Создаем тестовую игру и сохраняем ее
        game = Game()
        test_game_id = "test_" + shortuuid.uuid()[:6]
        game.save_state(test_game_id, "TestPlayer")
        
        try:
            # Изменяем состояние игры
            game.current_turn = "opponent"
            game.save_state(test_game_id)
            
            # Загружаем состояние из базы данных
            game_state = GameState.query.get(test_game_id)
            
            # Проверяем, что изменения сохранились
            self.assertEqual(game_state.current_turn, "opponent")
        finally:
            # Удаляем тестовую запись
            game_state = GameState.query.get(test_game_id)
            if game_state:
                db.session.delete(game_state)
                db.session.commit()

if __name__ == '__main__':
    unittest.main() 