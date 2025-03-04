let lastState = null;

async function fetchGameState() {
    const response = await fetch('/game/state');
    const data = await response.json();
    
    document.getElementById('turn').textContent = data.current_turn;
    
    if (lastState) {
        updateGameState(lastState, data);
    } else {
        renderInitialState(data);
    }
    
    lastState = data;
}

function renderInitialState(data) {
    // Рендерим карты игрока
    renderPlayerCards(data.player_cards);
    
    // Рендерим верхнюю карту
    renderTopCard(data.discard_pile);
    
    // Рендерим карты бота
    renderBotHand(data.bot_cards_count);
}

function updateGameState(oldState, newState) {
    // Обновляем карты игрока
    updatePlayerCards(oldState.player_cards, newState.player_cards);
    
    // Обновляем верхнюю карту
    updateTopCard(oldState.discard_pile, newState.discard_pile);
    
    // Обновляем карты бота
    updateBotHand(oldState.bot_cards_count, newState.bot_cards_count);
}

function renderPlayerCards(cards) {
    const container = document.getElementById('player-cards');
    container.innerHTML = '';
    
    cards.forEach(card => {
        const cardElement = createCardElement(card);
        cardElement.onclick = () => playCard(card);
        container.appendChild(cardElement);
    });
}

function updatePlayerCards(oldCards, newCards) {
    const container = document.getElementById('player-cards');
    
    // Удаляем карты, которых нет в новом состоянии
    Array.from(container.children).forEach(card => {
        const cardData = [card.textContent, card.dataset.verb, card.dataset.form];
        if (!newCards.some(newCard => 
            newCard[0] === cardData[0] && 
            newCard[1] === cardData[1] && 
            newCard[2] === cardData[2]
        )) {
            card.remove();
        }
    });
    
    // Добавляем новые карты
    newCards.forEach(newCard => {
        if (!Array.from(container.children).some(card => 
            card.textContent === newCard[0] && 
            card.dataset.verb === newCard[1] && 
            card.dataset.form === newCard[2]
        )) {
            const cardElement = createCardElement(newCard);
            cardElement.onclick = () => playCard(newCard);
            container.appendChild(cardElement);
        }
    });
}

function createCardElement(card) {
    const cardElement = document.createElement('div');
    cardElement.className = 'card';
    cardElement.textContent = card[0];
    cardElement.dataset.verb = card[1];
    cardElement.dataset.form = card[2];
    return cardElement;
}

function renderTopCard(card) {
    const discardPile = document.querySelector('.discard-pile');
    discardPile.innerHTML = '';
    
    const cardElement = createCardElement(card);
    cardElement.style.setProperty('--rotation', `${Math.random() * 4 - 2}deg`);
    discardPile.appendChild(cardElement);
}

function updateTopCard(oldCard, newCard) {
    if (oldCard[0] !== newCard[0] || oldCard[1] !== newCard[1] || oldCard[2] !== newCard[2]) {
        const discardPile = document.querySelector('.discard-pile');
        discardPile.innerHTML = ''; // Очищаем отбой перед добавлением новой карты
        
        const cardElement = createCardElement(newCard);
        cardElement.style.setProperty('--rotation', `${Math.random() * 4 - 2}deg`);
        discardPile.appendChild(cardElement);
        
        // Анимация появления карты
        cardElement.style.animation = 'playCard 0.5s ease forwards';
    }
}

function renderBotHand(count) {
    const botHand = document.querySelector('.bot-hand');
    botHand.innerHTML = '';
    
    // Создаем карты бота внахлест
    for (let i = 0; i < count; i++) {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.style.background = 'var(--card-back)';
        botHand.appendChild(cardElement);
    }
}

function updateBotHand(oldCount, newCount) {
    if (oldCount !== newCount) {
        renderBotHand(newCount);
    }
}

async function playCard(card) {
    try {
        const response = await fetch('/game/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card })
        });
        
        const result = await response.json();
        if(result.success) {
            await fetchGameState();
        }
        showNotification(result.message + (result.bot_message ? `\n${result.bot_message}` : ''));
    } catch (error) {
        showNotification('Error connecting to server');
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initial fetch
fetchGameState();
setInterval(fetchGameState, 5000); 