from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import json
import os
import shortuuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class GameState(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    deck = db.Column(db.JSON)
    player_cards = db.Column(db.JSON)
    bot_cards = db.Column(db.JSON)
    discard_pile = db.Column(db.JSON)
    current_turn = db.Column(db.String(10))

    def to_dict(self):
        return {
            "player_cards": self.player_cards,
            "bot_cards_count": len(self.bot_cards),
            "discard_pile": self.discard_pile[-1],
            "current_turn": self.current_turn
        }

def load_verbs():
    with open(os.path.join(app.static_folder, 'data', 'verbs.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['verbs']

@app.route("/")
def index():
    return render_template('index.html')

class Game:
    def __init__(self, game_id=None):
        self.verbs = load_verbs()
        if game_id:
            game_state = GameState.query.get(game_id)
            if game_state:
                self.deck = game_state.deck
                self.players = {
                    "player": game_state.player_cards,
                    "bot": game_state.bot_cards
                }
                self.discard_pile = game_state.discard_pile
                self.current_turn = game_state.current_turn
                return
        
        self.deck = []
        for verb in self.verbs:
            self.deck.extend([
                (verb['infinitive'], verb['infinitive'], 0),
                (verb['prasens_3'], verb['infinitive'], 1),
                (verb['prateritum'], verb['infinitive'], 2),
                (verb['partizip_2'], verb['infinitive'], 3)
            ])
        random.shuffle(self.deck)
        self.players = {"player": [], "bot": []}
        self.discard_pile = []
        self.current_turn = "player"
        self.deal_cards()

    def deal_cards(self):
        for _ in range(10):
            self.players["player"].append(self.deck.pop())
            self.players["bot"].append(self.deck.pop())
        self.discard_pile.append(self.deck.pop())

    def play_card(self, player, card):
        if player != self.current_turn:
            return False, "Not your turn!"
        if card not in self.players[player]:
            return False, "You don't have that card!"
        top_form, top_verb, top_index = self.discard_pile[-1]
        card_form, card_verb, card_index = card
        if card_index == top_index or card_verb == top_verb:
            self.players[player].remove(card)
            self.discard_pile.append(card)
            self.current_turn = "bot" if player == "player" else "player"
            return True, "Card played successfully."
        return False, "Invalid move!"

    def bot_move(self):
        if self.current_turn != "bot":
            return False, "Not bot's turn!"
        top_form, top_verb, top_index = self.discard_pile[-1]
        for card in self.players["bot"]:
            if card[2] == top_index or card[1] == top_verb:
                self.players["bot"].remove(card)
                self.discard_pile.append(card)
                self.current_turn = "player"
                return True, "Bot played a card."

        # if we are here this means that bot has no valid move
        self.pull_one_more_card("bot")
        return True, "Bot has no valid move. He takes the card and passes the move"

    def pull_one_more_card(self, player_name):
        self.players[player_name].append(self.deck.pop())
        self.current_turn = "bot" if player_name == "player" else "player"

    def get_state(self):
        return {
            "player_cards": self.players["player"],
            "bot_cards_count": len(self.players["bot"]),
            "discard_pile": self.discard_pile[-1],
            "current_turn": self.current_turn
        }

    def check_if_playable(self):
        top_form, top_verb, top_index = self.discard_pile[-1]
        for card in self.players["player"]:
            if card[2] == top_index or card[1] == top_verb:
                return True
        return False

    def save_state(self, game_id):
        game_state = GameState(
            id=game_id,
            deck=self.deck,
            player_cards=self.players["player"],
            bot_cards=self.players["bot"],
            discard_pile=self.discard_pile,
            current_turn=self.current_turn
        )
        db.session.merge(game_state)
        db.session.commit()

games = {}

@app.route("/game/new", methods=["POST"])
def create_new_game():
    game_id = shortuuid.uuid()[:8]
    games[game_id] = Game()
    games[game_id].save_state(game_id)
    return jsonify({"game_id": game_id})

@app.route("/game/<game_id>/state", methods=["GET"])
def get_game_state(game_id):
    if game_id not in games:
        games[game_id] = Game(game_id)
    
    game = games[game_id]
    if not game.check_if_playable():
        game.pull_one_more_card("player")
        bot_success, bot_message = game.bot_move()
        game.save_state(game_id)

    return jsonify(game.get_state())

@app.route("/game/<game_id>/play", methods=["POST"])
def play_card(game_id):
    if game_id not in games:
        return jsonify({"success": False, "message": "Game not found!"})
    
    game = games[game_id]
    data = request.json
    success, message = game.play_card("player", tuple(data["card"]))
    if success:
        bot_success, bot_message = game.bot_move()
        game.save_state(game_id)
        return jsonify({"success": success, "message": message, "bot_message": bot_message})
    return jsonify({"success": success, "message": message})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8085, debug=True)

