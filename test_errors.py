import unittest
from app import Game, GameState, db, app
import json

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
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
    
    def test_create_game_without_player_name(self):
        """Тест создания игры без имени игрока"""
        response = self.client.post('/game/new', json={'game_type': 'bot'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_join_game_without_player_name(self):
        """Тест присоединения к игре без имени игрока"""
        # Сначала создаем валидную игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'Player1', 'game_type': 'multiplayer'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Пытаемся присоединиться без имени
        join_response = self.client.post(f'/game/{game_id}/join', json={})
        join_data = json.loads(join_response.data)
        
        self.assertEqual(join_response.status_code, 200)
        self.assertFalse(join_data['success'])
        self.assertIn('message', join_data)
    
    def test_play_card_invalid_game(self):
        """Тест попытки сыграть карту в несуществующей игре"""
        response = self.client.post('/game/invalid_id/play', 
                              json={'card': ('Präsens', 'gehen', 0, 'идти'), 
                                   'player_name': 'TestPlayer'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_play_card_without_player_name(self):
        """Тест попытки сыграть карту без указания имени игрока"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Пытаемся сыграть карту без имени игрока
        play_response = self.client.post(f'/game/{game_id}/play', 
                                 json={'card': ('Präsens', 'gehen', 0, 'идти')})
        play_data = json.loads(play_response.data)
        
        self.assertEqual(play_response.status_code, 200)
        self.assertFalse(play_data['success'])
        self.assertIn('message', play_data)
    
    def test_play_invalid_card(self):
        """Тест попытки сыграть несуществующую карту"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Пытаемся сыграть карту, которой нет у игрока
        play_response = self.client.post(f'/game/{game_id}/play', 
                                 json={'card': ('Invalid', 'card', 999, 'invalid'), 
                                      'player_name': 'TestPlayer'})
        play_data = json.loads(play_response.data)
        
        self.assertEqual(play_response.status_code, 200)
        self.assertFalse(play_data['success'])
        self.assertIn('message', play_data)
    
    def test_draw_card_invalid_game(self):
        """Тест попытки взять карту в несуществующей игре"""
        response = self.client.post('/game/invalid_id/draw', 
                              json={'player_name': 'TestPlayer'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_draw_card_without_player_name(self):
        """Тест попытки взять карту без указания имени игрока"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'TestPlayer', 'game_type': 'bot'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Пытаемся взять карту без имени игрока
        draw_response = self.client.post(f'/game/{game_id}/draw', json={})
        draw_data = json.loads(draw_response.data)
        
        self.assertEqual(draw_response.status_code, 200)
        self.assertFalse(draw_data['success'])
        self.assertIn('message', draw_data)
    
    def test_join_as_bot(self):
        """Тест попытки присоединиться к игре с именем "bot"."""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'TestPlayer', 'game_type': 'multiplayer'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Пытаемся присоединиться с именем "bot"
        join_response = self.client.post(f'/game/{game_id}/join', 
                                    json={'player_name': 'bot'})
        join_data = json.loads(join_response.data)
        
        self.assertEqual(join_response.status_code, 200)
        self.assertFalse(join_data['success'])
        self.assertIn('message', join_data)
    
    def test_wrong_player_turn(self):
        """Тест попытки сделать ход, когда не твоя очередь"""
        # Создаем игру
        create_response = self.client.post('/game/new', 
                          json={'player_name': 'Player1', 'game_type': 'multiplayer'})
        create_data = json.loads(create_response.data)
        game_id = create_data['game_id']
        
        # Присоединяемся как второй игрок
        join_response = self.client.post(f'/game/{game_id}/join', 
                                    json={'player_name': 'Player2'})
        
        # Получаем состояние игры, чтобы определить чей ход
        state_response = self.client.get(f'/game/{game_id}/state?player_name=Player1')
        state_data = json.loads(state_response.data)
        
        # Если ход первого игрока, пытаемся сходить вторым игроком
        if state_data['current_turn'] == 'player':
            play_response = self.client.post(f'/game/{game_id}/play', 
                                     json={'card': ('Präsens', 'gehen', 0, 'идти'), 
                                          'player_name': 'Player2'})
            play_data = json.loads(play_response.data)
            
            self.assertEqual(play_response.status_code, 200)
            self.assertFalse(play_data['success'])
            self.assertIn('message', play_data)
        
        # Если ход второго игрока, пытаемся сходить первым игроком
        elif state_data['current_turn'] == 'opponent':
            play_response = self.client.post(f'/game/{game_id}/play', 
                                     json={'card': ('Präsens', 'gehen', 0, 'идти'), 
                                          'player_name': 'Player1'})
            play_data = json.loads(play_response.data)
            
            self.assertEqual(play_response.status_code, 200)
            self.assertFalse(play_data['success'])
            self.assertIn('message', play_data)

if __name__ == '__main__':
    unittest.main() 