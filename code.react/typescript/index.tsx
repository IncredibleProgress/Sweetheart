// a simple router for React components

import React from 'react'
import ReactDOM from 'react-dom'

import { WelcomePage } from './welcome'
import { NotificationPage } from './mtn-notifications'
import { WorkingTimePage } from './mtn-workingtime'

const App: React.FC = () => {
  // Get the current path from the URL
  const currentPath = window.location.pathname

  // Render different components based on the URL
  switch (currentPath) {
    case '/mtn/notification':
      return <NotificationPage />
    case '/mtn/workingtime':
      return <WorkingTimePage />
    default:
      return <WelcomePage /> }}

// render JSX and ReactApp
const app: HTMLElement | null = document.getElementById('ReactApp')
ReactDOM.createRoot(app!).render(<App />)
