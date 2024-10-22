import React from 'react'
import ReactDOM from 'react-dom/client'
import { WelcomePage } from './legacy.welcome'

// const APP_DATA = (await fetch("/data",{
//   method: "head",
//   headers: {"x-sweetheart-action":"fetch.init"} } )).json()

// console.log(APP_DATA)

function App() {

  switch (window.location.pathname) {
    // url based components rendering

    case '/welcome':
      return <WelcomePage />

    default: // Test page
      return(
        <div className="my-28">

          <h1 className="text-4xl lg:text-6xl text-pink-500 text-center italic">
            Welcome to Sweetheart </h1>

          <p className="text-center"><br/>
            get at {window.location.pathname} </p>

        </div>
      ) }}

// render JSX and ReactApp
const app: HTMLElement|null = document.getElementById('ReactApp')
ReactDOM.createRoot(app!).render(<App />)