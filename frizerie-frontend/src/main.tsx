import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import AuthProvider from './auth/AuthContext'
import { registerServiceWorker } from './services/swRegistration'

// Register service worker for offline support
registerServiceWorker()
  .then(registration => {
    if (registration) {
      console.log('Service worker registered successfully');
    }
  })
  .catch(error => {
    console.error('Service worker registration failed:', error);
  });

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
) 