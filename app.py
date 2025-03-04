from flask import Flask, request, jsonify, render_template
import random
import json
import os

app = Flask(__name__)

def load_verbs():
    with open(os.path.join(app.static_folder, 'data', 'verbs.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['verbs']

@app.route("/")
def index():
    return render_template('index.html')

class Game:
    def __init__(self):
        self.verbs = load_verbs()
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

game = Game()

@app.route("/game/state", methods=["GET"])
def get_game_state():
    if not game.check_if_playable():
       game.pull_one_more_card("player")
       bot_success, bot_message = game.bot_move()

    return jsonify(game.get_state())

@app.route("/game/play", methods=["POST"])
def play_card():
    data = request.json
    success, message = game.play_card("player", tuple(data["card"]))
    if success:
        bot_success, bot_message = game.bot_move()
        return jsonify({"success": success, "message": message, "bot_message": bot_message})
    return jsonify({"success": success, "message": message})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8085, debug=True)

