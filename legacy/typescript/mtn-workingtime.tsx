// Maintenance App - Working Time Table

import React from 'react'
import '../resources/tailwind.css'
import ReactDOM from 'react-dom/client'


// dataset

const days = Array(31).map((val,idx) => 
  <>
    <td>
      {idx+1}
      <input></input>
    </td><td>
      {idx+1}
      <input></input>
    </td>
  </> )


// export JSX

export const WorkingTimePage = () => { return(
<>
  <h1>Working Time Table</h1>
  <hr/>

  <div>
    <table><tr>
      <th>Jan</th>
      <th>Feb</th>
    </tr><tr>
      {days}
      {days}
    </tr></table>
  </div>
</> )}