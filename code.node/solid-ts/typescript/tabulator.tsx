import { onMount } from 'solid-js'
import { TabulatorFull } from 'tabulator-tables'
import '../node_modules/tabulator-tables/dist/css/tabulator_simple.min.css'

export interface DataRow {
  id: string | null
  [field: string]: string | number | null
}

async function fetchInit(url: string, config?, params?):
//NOTE: accept the tabulator ajaxRequestFunc signature
Promise<DataRow[]> {

  const connect = new URLSearchParams(params)
  const response = await fetch(
    `${url}?${connect.toString()}`, {
    headers: { 
      "accept": "application/json",
      "sweetheart-action": "fetch.rest" }
  })
  let json: DataRow[] = await response.json()
  if (json.length===0) { 
    json=[ { id: null, key: "", value: "" } ] 
  }
  return json
}

export const Tabulator = ()=> {

  // create reference (required):
  let tabulatorRef

  // create websocket connection:
  const ws = new WebSocket("http://127.0.0.1:8080/data")
  ws.onopen = () => {console.log('WebSocket connection open')}
  ws.onerror = () => {console.log('WebSocket connection error')}
  ws.onclose = () => {console.log('WebSocket connection closed')}

  // build custom real-time input editor:
  function rtInput
    (cell, onRendered, success, cancel, editorParams):
    HTMLInputElement {

    //create and style input
    const input = document.createElement("input")
    input.setAttribute("value", cell.getValue())
    input.setAttribute("type", "text")
    input.style.padding = "3px"

    function onChange() {
      ws.send(JSON.stringify({
        // head
        action: "ws.rest.patch",
        target: "test.testtable",
        // body
        id: cell.getRow().getData().id,
        name: cell.getField(),
        value: input.value
      }))
    }

    input.addEventListener("input", onChange)
    input.addEventListener("blur", ()=> success(input.value))
    return input
  }

  // create and mount tabulator table:
  onMount(() => {
    let table = new TabulatorFull( tabulatorRef,
      {
        ajaxURL: "http://127.0.0.1:8080/data",
        ajaxParams: { table:"testtable", database:"test" },
        ajaxRequestFunc: fetchInit,
        layout: "fitColumns",
        columns: [
          { title:"Id", field:"id", visible:false },
          { title:"Key", field:"key", editor: rtInput },
          { title:"Value", field:"value", editor: rtInput }
        ]
      })
  })
  return <div ref={tabulatorRef}></div>
}
