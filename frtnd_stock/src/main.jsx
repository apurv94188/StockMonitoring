// Entry point — mounts the React app into the <div id="root"> in index.html.
// StrictMode runs each component twice in development to surface side-effect bugs.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
