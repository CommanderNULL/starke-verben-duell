import React, { memo } from 'react';

// Используем React.memo для предотвращения ненужных перерисовок
const Card = memo(({ card, disabled = false, isDiscard = false, onClick }) => {
  // Получаем данные карты
  const [word, pos, difficulty, translation] = card;

  const handleClick = () => {
    if (!disabled && onClick) {
      onClick();
    }
  };

  // Используем CSS классы для стилизации карты
  const cardClass = `card ${disabled ? 'disabled' : ''} ${isDiscard ? 'discard' : ''}`;

  return (
    <div 
      className={cardClass} 
      onClick={handleClick}
    >
      {word}
      <div className="translation">{translation}</div>
    </div>
  );
}, (prevProps, nextProps) => {
  // Кастомная функция сравнения для мемоизации
  // Если card, disabled или isDiscard не изменились, не перерисовываем компонент
  return (
    prevProps.disabled === nextProps.disabled &&
    prevProps.isDiscard === nextProps.isDiscard &&
    JSON.stringify(prevProps.card) === JSON.stringify(nextProps.card)
  );
});

export default Card; 