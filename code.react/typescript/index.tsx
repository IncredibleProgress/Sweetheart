// a simple router for React components

import React from 'react'
import ReactDOM from 'react-dom'

import { WelcomePage } from './welcome'


const App: React.FC = () => {

  // Render different components based on the URL
  switch (window.location.pathname) {

    case '/welcome':
      return <WelcomePage />

    default: // Test page

      // const APP_DATA = (await fetch("/data",{
      //   method: "head",
      //   headers: {"x-sweetheart-action":"fetch.init"} } )).json()

      // console.log(APP_DATA)

      return(
        <div>
          <div className="my-28">
            <h1 className="text-5xl lg:text-8xl text-pink-500 text-center italic">
              Welcome to Sweetheart</h1>
          </div>

        </div>
      ) }}

// render JSX and ReactApp
const app: HTMLElement | null = document.getElementById('ReactApp')
ReactDOM.createRoot(app!).render(<App />)
