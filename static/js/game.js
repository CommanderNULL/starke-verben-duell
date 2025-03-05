let currentGameId = null;
let playerName = null;

async function createNewGame() {
    try {
        const name = document.getElementById('player-name').value.trim();
        if (!name) {
            notifications.show('Пожалуйста, введите ваше имя');
            return;
        }
        if (name.toLowerCase() === 'bot') {
            notifications.show('Имя "bot" зарезервировано');
            return;
        }
        
        const response = await fetch('/game/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ player_name: name })
        });
        const data = await response.json();
        if (data.success) {
            currentGameId = data.game_id;
            playerName = name;
            document.getElementById('current-game-id').textContent = currentGameId;
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('game-table').style.display = 'flex';
            updateGameState();
        } else {
            notifications.show(data.message);
        }
    } catch (error) {
        console.error('Error creating new game:', error);
        notifications.show('Ошибка при создании новой игры');
    }
}

async function joinGame() {
    const gameId = document.getElementById('game-id').value.trim();
    const name = document.getElementById('player-name').value.trim();
    
    if (!gameId) {
        notifications.show('Пожалуйста, введите ID игры');
        return;
    }
    if (!name) {
        notifications.show('Пожалуйста, введите ваше имя');
        return;
    }
    if (name.toLowerCase() === 'bot') {
        notifications.show('Имя "bot" зарезервировано');
        return;
    }
    
    try {
        const response = await fetch(`/game/${gameId}/join`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ player_name: name })
        });
        const data = await response.json();
        
        if (data.success) {
            currentGameId = gameId;
            playerName = name;
            document.getElementById('current-game-id').textContent = currentGameId;
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('game-table').style.display = 'flex';
            updateGameState();
        } else {
            notifications.show(data.message);
        }
    } catch (error) {
        console.error('Error joining game:', error);
        notifications.show('Ошибка при подключении к игре');
    }
}

async function updateGameState() {
    try {
        const response = await fetch(`/game/${currentGameId}/state`);
        const state = await response.json();
        updateUI(state);
    } catch (error) {
        console.error('Error updating game state:', error);
    }
}

async function playCard(card) {
    try {
        const response = await fetch(`/game/${currentGameId}/play`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ card })
        });
        const data = await response.json();
        if (data.success) {
            updateGameState();
        } else {
            notifications.show(data.message);
        }
    } catch (error) {
        console.error('Error playing card:', error);
        notifications.show('Ошибка при ходе');
    }
}

function updateUI(state) {
    // Обновляем карты игрока
    const playerHand = document.getElementById('player-cards');
    playerHand.innerHTML = '';
    state.player_cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.textContent = card[0];
        cardElement.onclick = () => playCard(card);
        playerHand.appendChild(cardElement);
    });

    // Обновляем карты бота
    const botHand = document.querySelector('.bot-hand');
    botHand.innerHTML = '';
    for (let i = 0; i < state.bot_cards_count; i++) {
        const cardElement = document.createElement('div');
        cardElement.className = 'card card-back';
        botHand.appendChild(cardElement);
    }

    // Обновляем верхнюю карту в сбросе
    const discardPile = document.querySelector('.discard-pile');
    discardPile.innerHTML = '';
    const topCard = document.createElement('div');
    topCard.className = 'card';
    topCard.textContent = state.discard_pile[0];
    discardPile.appendChild(topCard);

    // Обновляем индикатор хода
    const turnIndicator = document.getElementById('turn');
    turnIndicator.textContent = `Ход: ${state.current_turn === 'player' ? 'Игрок' : 'Бот'}`;
}

// Автоматическое обновление состояния игры каждые 2 секунды
setInterval(() => {
    if (currentGameId) {
        updateGameState();
    }
}, 2000); 