class Notification {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'error') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            padding: 12px 24px;
            border-radius: 4px;
            background-color: ${type === 'error' ? '#ff4444' : '#4CAF50'};
            color: white;
            font-size: 14px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        this.container.appendChild(notification);

        // Добавляем стили для анимации
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateY(-100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                this.container.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Создаем глобальный экземпляр
window.notifications = new Notification(); 