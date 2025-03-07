import unittest
import json
from app import app, db, GameState

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Настраиваем тестовый клиент и контекст приложения
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_route(self):
        """Проверка доступности главной страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_new_game(self):
        """Проверка создания новой игры"""
        response = self.client.post('/game/new', 
                            json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('game_id', data)
        
        # Проверяем, что запись была создана в базе данных
        game_id = data['game_id']
        game_state = GameState.query.get(game_id)
        self.assertIsNotNone(game_state)
        self.assertEqual(game_state.player_name, 'TestPlayer')
        self.assertEqual(game_state.game_type, 'bot')
    
    def test_create_multiplayer_game(self):
        """Проверка создания многопользовательской игры"""
        response = self.client.post('/game/new', 
                      json={'player_name': 'TestPlayer', 'game_type': 'multiplayer'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Проверяем, что игра находится в состоянии ожидания
        game_id = data['game_id']
        game_state = GameState.query.get(game_id)
        self.assertEqual(game_state.game_status, 'waiting')
    
    def test_join_game(self):
        """Проверка присоединения к существующей игре"""
        # Сначала создаем игру
        create_response = self.client.post('/game/new', 
                        json={'player_name': 'Player1', 'game_type': 'multiplayer'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Теперь присоединяемся к игре
        join_response = self.client.post(f'/game/{game_id}/join', 
                                    json={'player_name': 'Player2'})
        join_data = json.loads(join_response.data)
        
        self.assertEqual(join_response.status_code, 200)
        self.assertTrue(join_data['success'])
        
        # Проверяем, что игра теперь активна
        game_state = GameState.query.get(game_id)
        self.assertEqual(game_state.game_status, 'active')
        self.assertEqual(game_state.opponent_name, 'Player2')
    
    def test_get_game_state(self):
        """Проверка получения состояния игры"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                         json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Получаем состояние игры
        state_response = self.client.get(f'/game/{game_id}/state?player_name=TestPlayer')
        state_data = json.loads(state_response.data)
        
        self.assertEqual(state_response.status_code, 200)
        self.assertIn('player_cards', state_data)
        self.assertIn('opponent_cards_count', state_data)
        self.assertIn('discard_pile', state_data)
        self.assertIn('current_turn', state_data)
    
    def test_play_card(self):
        """Проверка игры картой (базовый случай)"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                         json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Получаем состояние игры для определения доступных карт
        state_response = self.client.get(f'/game/{game_id}/state?player_name=TestPlayer')
        state_data = json.loads(state_response.data)
        
        # Проверяем, есть ли карты у игрока
        if state_data['player_cards'] and len(state_data['player_cards']) > 0:
            top_card = state_data['discard_pile']
            
            # Ищем карту, которую можно сыграть
            playable_card = None
            for card in state_data['player_cards']:
                if card[1] == top_card[1] or card[2] == top_card[2]:
                    playable_card = card
                    break
            
            if playable_card:
                # Играем картой
                play_response = self.client.post(f'/game/{game_id}/play', 
                                  json={'card': playable_card, 'player_name': 'TestPlayer'})
                play_data = json.loads(play_response.data)
                
                # Проверяем результат
                self.assertEqual(play_response.status_code, 200)
                self.assertIn('success', play_data)
    
    def test_draw_card(self):
        """Проверка взятия карты, когда нет возможности сходить"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                         json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Получаем состояние игры
        state_response = self.client.get(f'/game/{game_id}/state')
        state_data = json.loads(state_response.data)
        
        # Первый ход обычно у игрока, пытаемся взять карту
        # (Этот тест вероятностный, он может проходить или нет,
        #  в зависимости от того, есть ли у игрока возможность сходить)
        draw_response = self.client.post(f'/game/{game_id}/draw', 
                             json={'player_name': 'TestPlayer'})
        draw_data = json.loads(draw_response.data)
        
        # Просто проверяем, что ответ имеет правильный формат
        self.assertEqual(draw_response.status_code, 200)
        self.assertIn('success', draw_data)
        self.assertIn('message', draw_data)
    
    def test_join_nonexistent_game(self):
        """Проверка попытки присоединиться к несуществующей игре"""
        response = self.client.post('/game/nonexistent/join', 
                               json={'player_name': 'TestPlayer'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_get_nonexistent_game_state(self):
        """Проверка попытки получить состояние несуществующей игры"""
        response = self.client.get('/game/nonexistent/state')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main() 