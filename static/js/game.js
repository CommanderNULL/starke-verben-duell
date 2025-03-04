async function fetchGameState() {
    const response = await fetch('/game/state');
    const data = await response.json();
    
    document.getElementById('turn').textContent = data.current_turn;
    document.getElementById('discard').textContent = data.discard_pile[0];
    document.getElementById('bot-count').textContent = data.bot_cards_count;
    document.getElementById('cards-count').textContent = data.player_cards.length;
    
    renderPlayerCards(data.player_cards);
}

function renderPlayerCards(cards) {
    const container = document.getElementById('player-cards');
    container.innerHTML = '';
    
    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.textContent = card[0];
        cardElement.onclick = () => playCard(card);
        
        container.appendChild(cardElement);
    });
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
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.left = '50%';
    notification.style.transform = 'translateX(-50%)';
    notification.style.background = 'var(--accent)';
    notification.style.color = 'white';
    notification.style.padding = '1rem 2rem';
    notification.style.borderRadius = '25px';
    notification.style.boxShadow = '0 4px 6px rgba(0,0,0,0.2)';
    notification.style.animation = 'slideIn 0.3s ease';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initial fetch
fetchGameState();
setInterval(fetchGameState, 5000); 