import React, { useEffect, useState } from 'react';
import { CSSTransition } from 'react-transition-group';

const Notification = ({ message, isConfirmation = false, onConfirm = null, onClose }) => {
  const [visible, setVisible] = useState(true);

  // Для обычных уведомлений автоматически скрываем через 3 секунды
  useEffect(() => {
    if (!isConfirmation) {
      const timer = setTimeout(() => {
        setVisible(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [isConfirmation]);

  // Обработчик подтверждения
  const handleConfirm = () => {
    setVisible(false);
    if (onConfirm) onConfirm();
  };

  // Обработчик закрытия
  const handleClose = () => {
    setVisible(false);
    if (onClose) onClose();
  };

  // Эффект анимации исчезновения перед удалением из DOM
  const handleExited = () => {
    if (onClose) onClose();
  };

  return (
    <CSSTransition
      in={visible}
      timeout={300}
      classNames="notification"
      unmountOnExit
      onExited={handleExited}
    >
      <div className={`notification ${isConfirmation ? 'confirmation' : ''}`}>
        <p>{message}</p>
        
        {isConfirmation && (
          <>
            <p>Хотите начать новую игру?</p>
            <div className="notification-buttons">
              <button onClick={handleConfirm}>Новая игра</button>
              <button onClick={handleClose}>Отмена</button>
            </div>
          </>
        )}
      </div>
    </CSSTransition>
  );
};

export default Notification; 