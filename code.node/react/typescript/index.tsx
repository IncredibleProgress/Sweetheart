import React from 'react'
import ReactDOM from 'react-dom/client'

import '../resources/tailwind.css'
import { WelcomePage } from './welcome'

function App() {

  switch(window.location.pathname) {

    case "/welcome": 
      return(<WelcomePage/>)

    default:
      return(
        <div className="my-28">

          <h1 className="text-4xl lg:text-6xl text-pink-500 text-center italic">
            Welcome to Sweetheart </h1>

          <p className="text-center"><br/>
            get at {window.location.pathname} </p>
        </div> )}
}

const elmt = document.getElementById('webapp')
ReactDOM.createRoot(elmt!).render(<App/>)