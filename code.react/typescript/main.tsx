// Maintenance App Refactory

import React from 'react'
import '../resources/tailwind.css'
import ReactDOM from 'react-dom/client'
import { Title,TextInput } from './components'

function Notification():
  React.JSX.Element {
    
  return(
    <div className="p-14 space-y-2 max-w-lg m-auto">
      
      <Title className="text-center">
        Demande d'intervention</Title>

      <div className="flex mt-12">
        <TextInput/>
        {/* <SelectOption/> */}
      </div>

      <div className="flex mt-2">
        <select id=""
          className="border rounded-b-md px-3 py-2 focus:outline-none focus:border-pink-600">
          <option></option>
        </select>
        <select id=""
          className="w-24 mr-1 border rounded-b-md px-3 py-2 focus:outline-none focus:border-pink-600">
          <option></option>
        </select>

        <input id="" type="text" className="flex-initial w-24 text-center"
          placeholder="criticité"/>
      </div>

      <textarea id=""
        className="w-full border rounded-b-md px-3 py-2 focus:outline-none focus:border-pink-600"
        placeholder="insert a description">
      </textarea>
    </div>
  )
}

// set title from the first <h1> element
const heading = document.getElementsByTagName("h1")[0]
if (heading != null) document.title = heading.innerText

// render the React app
const app: HTMLElement | null = document.getElementById('ReactApp')
ReactDOM.createRoot(app!).render(<Notification />)
