import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './components/App';

// Рендерим приложение после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}); 