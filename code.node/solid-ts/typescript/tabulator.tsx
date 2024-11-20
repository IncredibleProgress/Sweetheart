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


export const Tabulator = () => {

  let tabulatorRef
  // const [ hub, load ] = useDataHub("testtable")
  // const [ data, { mutate, refetch } ] = createResource(load)
  
  onMount(() => {
    let table = new TabulatorFull(
      tabulatorRef, {
        ajaxURL: "http://127.0.0.1:8080/data",
        ajaxParams: {table:"testtable",database:"test"},
        ajaxRequestFunc: fetchInit,
        layout: "fitColumns",
        columns: [
          { title:"Key", field:"key", editor:"input" },
          { title:"Value", field:"value", editor:"input" }
        ]
      })
  })

  return <div ref={tabulatorRef}></div>
}
