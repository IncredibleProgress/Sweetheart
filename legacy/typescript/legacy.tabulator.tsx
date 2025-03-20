import { onMount } from 'solid-js'
import * as datasystem from './datasystem'
import { TabulatorFull } from 'tabulator-tables'
import '../node_modules/tabulator-tables/dist/css/tabulator.min.css'


// set tabulator table as solid-js component:
export const Tabulator = ()=> {

  let tabulatorRef //! required 
  const ws = new datasystem.WebSocket()

  async function fetchData(url, config, params) {
    // allow fetching data from http REST API
    //NOTE: takes tabulator ajaxRequestFunc signature but config is not used

    const target = new URLSearchParams(params)
    this.currentTarget = `${params.database}.${params.table}`

    return await fetch(`${url}?${target.toString()}`, {
      headers: { 
        "accept": "application/json",
        "sweetheart-action": "fetch.rest" }
    }).then(response => response.json())
  }

  function rtInput
  // real-time tabulator input editor
  (cell, onRendered, success, cancel, editorParams): HTMLInputElement {

    const input = document.createElement("input")
    input.setAttribute("value", cell.getValue())
    input.setAttribute("type", "text")
    input.style.padding = "3px"

    function onChange() {

      if (!ws.currentTarget) { 
        throw "No target set for real-time data update"
      }

      const rowID = cell.getRow().getData().id
      if (!rowID) {
        // insert new row
        ws.send(JSON.stringify({
          // head-like
          action: "ws.rest.post",
          target: ws.currentTarget,
          // body-like
          key: cell.getField(),
          value: input.value
        }))
      } else {
        // update existing row
        ws.send(JSON.stringify({
          // head-like
          action: "ws.rest.patch",
          target: ws.currentTarget,
          // body-like
          id: rowID,
          name: cell.getField(),
          value: input.value
        }))
      }}

    input.addEventListener("input", onChange)
    input.addEventListener("blur", ()=> success(input.value))
    return input
  }

  // create and mount tabulator table:
  onMount(() => {
    let table = new TabulatorFull( tabulatorRef,
      {
        ajaxURL: datasystem.source("http"),
        ajaxParams: { table:"testtable", database:"test" },
        ajaxRequestFunc: fetchData,// switch to http REST API
        layout: "fitColumns",
        tabEndNewRow: { id:0, key:"", value:"" },
        columns: [
          { title:"Id", field:"id", visible:false },
          { title:"Key", field:"key", editor: rtInput },
          { title:"Value", field:"value", editor: rtInput }
        ]
      })
  })
  return <div ref={tabulatorRef}></div>
}
