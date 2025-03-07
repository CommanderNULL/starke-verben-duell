let currentGameId = null;
let playerName = null;
let gameType = 'bot';
let isMyTurn = false;

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
        
        gameType = document.querySelector('input[name="game-type"]:checked').value;
        
        const response = await fetch('/game/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                player_name: name,
                game_type: gameType
            })
        });
        const data = await response.json();
        if (data.success) {
            currentGameId = data.game_id;
            playerName = name;
            document.getElementById('current-game-id').textContent = currentGameId;
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('game-table').style.display = 'flex';
            document.getElementById('player-name-display').textContent = name;
            
            if (gameType === 'multiplayer') {
                notifications.show('Игра создана! Поделитесь ID игры с противником: ' + currentGameId);
            }
            
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
            gameType = data.game_type;
            document.getElementById('current-game-id').textContent = currentGameId;
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('game-table').style.display = 'flex';
            document.getElementById('player-name-display').textContent = name;
            document.getElementById('opponent-name').textContent = data.opponent_name;
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
    if (!currentGameId || !playerName) return;

    try {
        const url = `/game/${currentGameId}/state?player_name=${encodeURIComponent(playerName)}&t=${Date.now()}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        const state = await response.json();
        
        // Логирование состояния для отладки
        console.log('Получено состояние игры:', state);
        
        if (state.status === 'waiting') {
            document.getElementById('waiting-message').style.display = 'block';
            document.querySelector('.opponent-hand').style.display = 'none';
            document.getElementById('opponent-name').textContent = 'Ожидание противника...';
            return;
        }
        
        document.getElementById('waiting-message').style.display = 'none';
        document.querySelector('.opponent-hand').style.display = 'flex';
        
        if (state.opponent_name) {
            document.getElementById('opponent-name').textContent = state.opponent_name;
        }
        
        // Убедимся, что isMyTurn корректно установлен в любом типе игры
        if (gameType === 'bot') {
            // В игре с ботом наш ход, если current_turn === 'player'
            isMyTurn = state.current_turn === 'player';
        } else {
            // В мультиплеере используем is_my_turn из состояния
            isMyTurn = state.is_my_turn;
        }
        
        // Проверяем, закончена ли игра
        if (state.game_over) {
            let message = '';
            if (state.winner === 'player') {
                message = 'Поздравляем! Вы выиграли, избавившись от всех карточек!';
            } else if (state.winner === 'opponent') {
                message = 'Противник выиграл, избавившись от всех карточек!';
            }
            
            notifications.show(message);
            
            // Для игры с ботом предлагаем начать новую игру
            if (state.game_type === 'bot') {
                // Создаем уведомление с кнопкой "Новая игра"
                const notification = document.createElement('div');
                notification.className = 'notification confirmation';
                notification.innerHTML = `
                    <p>${message}</p>
                    <p>Хотите начать новую игру?</p>
                    <div class="notification-buttons">
                        <button id="new-game-btn">Новая игра</button>
                        <button id="cancel-new-game-btn">Отмена</button>
                    </div>
                `;
                document.body.appendChild(notification);
                
                // Обработчики событий для кнопок
                document.getElementById('new-game-btn').onclick = () => {
                    notification.remove();
                    document.getElementById('game-setup').style.display = 'block';
                    document.getElementById('game-table').style.display = 'none';
                    document.getElementById('player-name').value = playerName; // Сохраняем имя игрока
                    document.querySelector('input[value="bot"]').checked = true; // Выбираем игру с ботом
                };
                
                document.getElementById('cancel-new-game-btn').onclick = () => {
                    notification.remove();
                };
            }
        }
        
        updateUI(state);
        
        // Проверяем, может ли игрок сделать ход
        if (isMyTurn && state.player_cards && Array.isArray(state.player_cards)) {
            const hasValidMove = checkIfHasValidMove(state.player_cards, state.discard_pile);
            // Показываем кнопку взятия карты только если сейчас ход игрока и у него нет валидных ходов
            document.getElementById('draw-button').style.display = isMyTurn && !hasValidMove && !state.game_over ? 'block' : 'none';
        } else {
            document.getElementById('draw-button').style.display = 'none';
        }
    } catch (error) {
        console.error('Error updating game state:', error);
    }
}

// Функция для проверки наличия валидного хода
function checkIfHasValidMove(playerCards, discardPile) {
    if (!playerCards || !discardPile) return false;
    const topCard = discardPile;
    const topForm = topCard[0];
    const topVerb = topCard[1];
    const topIndex = topCard[2];
    
    for (const card of playerCards) {
        if (card[2] === topIndex || card[1] === topVerb) {
            return true;
        }
    }
    return false;
}

// Функция для взятия карты
async function drawCard() {
    try {
        const response = await fetch(`/game/${currentGameId}/draw`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                player_name: playerName
            })
        });
        const data = await response.json();
        if (data.success) {
            if (data.bot_message) {
                notifications.show(data.bot_message);
            }
            notifications.show(data.message);
            updateGameState();
        } else {
            notifications.show(data.message);
        }
    } catch (error) {
        console.error('Error drawing card:', error);
        notifications.show('Ошибка при взятии карты');
    }
}

async function playCard(card) {
    if (!isMyTurn) {
        notifications.show('Сейчас не ваш ход!');
        return;
    }
    
    try {
        const response = await fetch(`/game/${currentGameId}/play`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                card,
                player_name: playerName
            })
        });
        const data = await response.json();
        if (data.success) {
            if (data.bot_message) {
                notifications.show(data.bot_message);
            }
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
    
    if (state.player_cards && Array.isArray(state.player_cards)) {
        state.player_cards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            if (!isMyTurn || state.game_over) {
                cardElement.classList.add('disabled');
            }
            cardElement.textContent = card[0];
            
            // Добавляем перевод
            const translationElement = document.createElement('div');
            translationElement.className = 'translation';
            translationElement.textContent = card[3];
            cardElement.appendChild(translationElement);
            
            // Сохраним все данные карты как атрибуты для точного соответствия при отправке
            cardElement.dataset.word = card[0];
            cardElement.dataset.pos = card[1];
            cardElement.dataset.difficulty = card[2];
            cardElement.dataset.translation = card[3];
            
            // При клике отправляем карту в точном формате как она получена с сервера
            if (!state.game_over) {
                cardElement.onclick = () => playCard(card);
            }
            playerHand.appendChild(cardElement);
        });
    }

    // Обновляем карты противника
    const opponentHand = document.querySelector('.opponent-hand');
    opponentHand.innerHTML = '';
    const opponentCount = state.opponent_cards_count || 0;
    for (let i = 0; i < opponentCount; i++) {
        const cardElement = document.createElement('div');
        cardElement.className = 'card card-back';
        opponentHand.appendChild(cardElement);
    }

    // Обновляем счетчики карт
    document.getElementById('player-cards-count').textContent = state.player_cards ? state.player_cards.length : 0;
    document.getElementById('opponent-cards-count').textContent = state.opponent_cards_count || 0;

    // Обновляем верхнюю карту в сбросе
    const discardPile = document.querySelector('.discard-pile');
    discardPile.innerHTML = '';
    
    if (state.discard_pile) {
        const topCard = document.createElement('div');
        topCard.className = 'card';
        topCard.textContent = state.discard_pile[0];
        
        // Добавляем перевод для верхней карты
        const topTranslationElement = document.createElement('div');
        topTranslationElement.className = 'translation';
        topTranslationElement.textContent = state.discard_pile[3];
        topCard.appendChild(topTranslationElement);
        
        discardPile.appendChild(topCard);
    }

    // Обновляем индикатор хода
    const turnIndicator = document.getElementById('turn');
    if (state.game_over) {
        const winner = state.winner === 'player' ? 'Вы выиграли!' : 'Противник выиграл!';
        turnIndicator.textContent = `Игра окончена. ${winner}`;
    } else if (gameType === 'bot') {
        // Для игры с ботом просто проверяем, чей ход
        turnIndicator.textContent = `Ход: ${state.current_turn === 'player' ? 'Ваш' : 'Противника'}`;
    } else {
        // Для мультиплеерной игры используем is_my_turn
        turnIndicator.textContent = `Ход: ${state.is_my_turn ? 'Ваш' : 'Противника'}`;
    }
}

// Автоматическое обновление состояния игры каждые 2 секунды
setInterval(() => {
    if (currentGameId) {
        updateGameState();
    }
}, 2000); 