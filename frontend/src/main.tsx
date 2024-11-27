import React from 'react'
import ReactDOM from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

<<<<<<< HEAD
=======
// Log environment info
console.log('🌍 Environment:', {
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  mode: import.meta.env.MODE,
  apiUrl: import.meta.env.VITE_API_URL,
  clerkKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.substring(0, 10) + '...'
});

>>>>>>> origin
if (!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY in environment')
}

<<<<<<< HEAD
=======
if (!import.meta.env.VITE_API_URL) {
  throw new Error('Missing VITE_API_URL in environment')
}

>>>>>>> origin
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ClerkProvider>
  </React.StrictMode>,
)
