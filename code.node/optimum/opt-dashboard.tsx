// Shopfloor Management Dashboard

import React from 'react'
import '../resources/tailwind.css'

import LineChart from './linechart'
import BarChart from './barchart'
import PieChart from './piechart'

// set data models

class IncomingTask {
  scheduling: "now" | "24h" | "48h" | "later"
  status: "pending" | "ongoing" | "done" | "canceled"
  type: "Safe" | "Food" | "Proc" | "Mtce" | "Walk"
  description: string
  textarea: string
  completed: Date }

class PerformanceRate {
  rate: number
  target: number // green area
  alert: number // yellow area
  alarm: number // red are
  message: string }

// set svg icons

function StatusIcon({status,...props}): JSX.Element {
  switch (status) {
    case "pending": // red bell icon
      return <svg {...props} viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round"></g><g> <g> <path fill="#ff0000" d="M56,44c-1.832,0-4-2.168-4-4V20C52,8.973,43.027,0,32,0S12,8.973,12,20v20c0,1.793-2.207,4-4,4 c-2.211,0-4,1.789-4,4s1.789,4,4,4h48c2.211,0,4-1.789,4-4S58.211,44,56,44z"></path> <path fill="#ff0000" d="M32,64c4.418,0,8-3.582,8-8H24C24,60.418,27.582,64,32,64z"></path> </g> </g></svg>
    case "ongoing": // yellow clock icon
      return <svg {...props} viewBox="0 0 22 22" fill="#d16500" stroke="#d16500" stroke-width="0.24" xmlns="http://www.w3.org/2000/svg"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round"></g><g> <path d="M12 21a9 9 0 1 1 9-9 9.01 9.01 0 0 1-9 9zm0-16a7 7 0 1 0 7 7 7.008 7.008 0 0 0-7-7z"></path> <path d="M15.03 14.75a1 1 0 0 1-.5-.134l-3.03-1.75A1 1 0 0 1 11 12V7.5a1 1 0 0 1 2 0v3.923l2.531 1.461a1 1 0 0 1-.501 1.866z"></path> </g></svg>
    case "done": // green check icon
      return <svg {...props} viewBox="0 0 22 22" fill="#118f00" stroke="#118f00" stroke-width="0.24" xmlns="http://www.w3.org/2000/svg"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round"></g><g> <path d="M9.172 18.657a1 1 0 0 1-.707-.293l-5.657-5.657a1 1 0 0 1 1.414-1.414l4.95 4.95L19.778 5.636a1 1 0 0 1 1.414 1.414L9.879 18.364a1 1 0 0 1-.707.293z"></path> </g></svg>
    case "canceled": // black cross icon
      return <svg {...props} viewBox="0 0 22 22" fill="#000000"><g stroke-width="0" xmlns="http://www.w3.org/2000/svg"></g><g stroke-linecap="round" stroke-linejoin="round"></g><g> <path d="M13.414 12l4.95-4.95a1 1 0 0 0-1.414-1.414L12 10.586l-4.95-4.95A1 1 0 0 0 5.636 7.05l4.95 4.95-4.95 4.95a1 1 0 0 0 1.414 1.414l4.95-4.95 4.95 4.95a1 1 0 0 0 1.414-1.414z"></path> </g></svg>
  }}

// set single components

function TaskItem({task,...props}): JSX.Element {
  props.className = `${props.className||""} flex`
  return <div {...props}>
    <p className="text-xl w-5/6 ml-2">{task.description}</p>
    {/* <p className="text-lg w-1/6 ml-2">{task.type}</p> */}
    {/* <p className="text-lg w-1/4 ml-2">{task.scheduling}</p> */}
    <StatusIcon className="w-1/6 my-1" status={task.status} />
    {/* <input type="checkbox" className="w-1/12 mx-4" /> */}
  </div> }


// provide some dummy dataset

const sampleData = [
  { date: '2023-01-01', value: 820 },
  { date: '2023-02-01', value: 932 },
  { date: '2023-03-01', value: 901 },
  { date: '2023-04-01', value: 934 },
  { date: '2023-05-01', value: 1290 },
  { date: '2023-06-01', value: 1330 },
  { date: '2023-07-01', value: 1320 } ]

const safetyTasks: IncomingTask[] = [
  {scheduling:"now",status:"pending",type:"Safe",description:"Oil on the floor to clean",textarea:"",completed:new Date()},
  {scheduling:"24h",status:"pending",type:"Safe",description:"Fire extinguisher to check",textarea:"",completed:new Date()},
  {scheduling:"later",status:"ongoing",type:"Safe",description:"Emergency exit to clear",textarea:"",completed:new Date()},
  ]

///////////////////////////////////////////////////////////////////////////////
// Shopfloor Management Component ////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

export function Dashboard(): JSX.Element {
  return <div className="h-full m-4">
  
    <h1 className="text-6xl text-center italic text-green-900 background-green-100">
      OPTIMUM Shopfloor Management </h1>

    <hr className="w-full mt-4 mb-2" />

    <div className="flex mt-4">

      {/* col 1 on 3 */}
      <div className="w-1/3 border border-2 border-green-600 rounded-lg p-2 mr-2">

        <h2 className="text-4xl text-center text-red-600 mb-4">
          Security </h2>

        <div className="flex mt-8 mb-2">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Open issues</p>
            <p className="w-20 text-2xl text-center border border-red-800 rounded-lg p-1">3</p>
          </div>
        </div>

        <div className="flex mt-2 mb-8">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Ongoing actions</p>
            <p className="w-20 text-2xl text-center border border-yellow-600 rounded-lg p-1">1</p>
          </div>
        </div>

        <TaskItem task={safetyTasks[0]} className="h-12 border border-4 border-red-800 rounded-lg p-2 mx-2 mb-1" />
        <TaskItem task={safetyTasks[1]} className="h-12 border border-4 border-red-800 rounded-lg p-2 mx-2 mb-1" />
        <TaskItem task={safetyTasks[2]} className="h-12 border border-2 border-red-800 rounded-lg p-2 mx-2 mb-8" />

        <hr className="w-full my-2" />

        <h2 className="text-4xl text-center text-green-700 mt-8 mb-4">
          Quality</h2>

        <div className="flex mt-8 mb-2">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Sugar</p>
            <p className="w-20 text-2xl text-center bg-green-400 border rounded-lg p-1">OK</p>
          </div>
        </div>

        <div className="flex mt-2 mb-2">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Thick juice</p>
            <p className="w-20 text-2xl text-center bg-red-400 border rounded-lg p-1">NC</p>
          </div>
        </div>

        <div className="flex mt-2 mb-2">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Pulps</p>
            <p className="w-20 text-2xl text-center bg-green-400 border rounded-lg p-1">OK</p>
          </div>
        </div>

        <div className="flex mt-2 mb-8">
          <div className="flex mx-auto">
            <p className="w-64 text-2xl">Molasses</p>
            <p className="w-20 text-2xl text-center bg-green-400 border rounded-lg p-1">OK</p>
          </div>
        </div>

        <br/>
        <h3 className="text-xl">thick juice quality trends - non conformity</h3>
        <LineChart data={sampleData} width={600} height={148} />

      </div>

      {/* col 2 on 3 */}
      <div className="w-1/3 border border-2 border-green-600 rounded-lg p-2 mr-2">
      
        <h2 className="text-3xl text-center mb-4">
          Production Rates </h2>

        <br/>
        <h3 className="text-xl">tons of beets</h3>
        <LineChart data={sampleData} width={600} height={148} />
        <br/>
        <h3 className="text-xl">tons of sugar</h3>
        <LineChart data={sampleData} width={600} height={148} />

        <hr className="w-full my-2" />

        <h2 className="text-3xl text-center mb-4">
          Consumptions </h2>
        
        <br/>
        <h3 className="text-xl">energy last 24h</h3>
        <LineChart data={sampleData} width={600} height={148} />

        <br/>
        <h3 className="text-xl">auxilaries</h3>
        <BarChart data={[
          { name: 'A', value: 30 },
          { name: 'B', value: 80 },
          { name: 'C', value: 45 },
          { name: 'D', value: 60 },
          { name: 'E', value: 20 },
          { name: 'F', value: 90 },
          { name: 'G', value: 55 } ]} />

      </div>

      {/* col 3 on 3 */}
      <div className="w-1/3 border border-2 border-green-600 rounded-lg p-2 mr-2">

        <h2 className="text-3xl text-center mb-4">
          Ongoing Actions List </h2>

        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-1" 
          task={{scheduling:"24h",status:"pending",type:"Food",description:"Steam cleaning centrifuge 1st1",textarea:"",completed:new Date()}} />
        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-4" 
          task={{scheduling:"24h",status:"pending",type:"Walk",description:"Beets pumps n°1 blocked",textarea:"",completed:new Date()}} />

        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-1" 
          task={{scheduling:"24h",status:"ongoing",type:"Walk",description:"Next beets washing area tour",textarea:"",completed:new Date()}} />
        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-1" 
          task={{scheduling:"24h",status:"ongoing",type:"Mtce",description:"Gas pipe vibrations to fix",textarea:"",completed:new Date()}} />

        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-4" 
          task={{scheduling:"24h",status:"done",type:"Prod",description:"Restart soda injection",textarea:"",completed:new Date()}} />

        <hr className="w-full my-8" />

        <h2 className="text-3xl text-center mt-2 mb-4">
          Trainings follow-up </h2>

        <TaskItem className="h-12 border border-gray-500 rounded-lg p-2 mx-2 mb-4" 
          task={{scheduling:"24h",status:"ongoing",type:"Prod",description:"last trainings to achieve in the next 48h",textarea:"",completed:new Date()}} />
        
        <div className="ml-24">
          <PieChart data={[
            { name: 'achieved', value: 80 },
            { name: 'not achieved', value: 20 } ]} />
        </div>
        
      </div>

    </div>
    <hr className="w-full my-4" />

  </div>}