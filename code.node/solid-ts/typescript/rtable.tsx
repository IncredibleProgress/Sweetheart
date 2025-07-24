import '../resources/tailwind.css'
import * as datasystem from './datasystem'
import { For, Suspense, createResource } from 'solid-js'

// TailwindCss classes
// https://play.tailwindcss.com

const tw = {
  handler: "w-3 border border-white bg-gray-200 hover:bg-pink-200",// row handler
  header: "border border-white font-semibold bg-gray-200",
  data: "w-32 p-1 border text-center",// default cell class
  input: "w-32 px-1 focus:outline-2 focus:outline-pink-400" 
}

// Data types and columns settings
// https://www.typescriptlang.org/docs/handbook/2/everyday-types.html

type DataRow = {
  id: number | string
  [key: string]: string | number | null
}

type TableColumn = {
  header: string
  fieldname: string
  input?: string
  class?: string  // TwCss cell class
  iclass?: string // TwCss input class
  hidden?: boolean
}

const columns: TableColumn[] =  [
  // { header: "Id", name: "id", hidden: true },
  { header: "Name", fieldname: "key", class: tw.data, iclass: tw.input },
  { header: "Value", fieldname: "value", class: tw.data, iclass: tw.input } 
]

// Real-time Table Component
// https://docs.solidjs.com

export const RtTable = (table: string = "testtable") => {

  const ws = new datasystem.WebSocket()
  const [ data ] = createResource(() => ws.fetchTable(table))

  return (
    <Suspense fallback={ <div class="m-2">loading...</div> }>
      <table>
        <thead>
          <tr>
            <th class={ tw.header }></th>
            <For each={ columns }>
              {(column: TableColumn) => (  
                <th class={ tw.header }>{ column.header }</th> )}
            </For>
          </tr>
        </thead>
        <tbody>
          <For each={data() as DataRow[]}>
            {(row: DataRow) => (
              <tr>
                <td 
                  class={ tw.handler }
                  data-rowid={ row.id }
                  // oncontextmenu={evt => onContextMenu(evt.currentTarget)}
                ></td>
                <For each={ columns }>
                  {(column: TableColumn) => (
                    <td
                      class={ column.class }
                      hidden={ column.hidden }
                      // style={{ display: column.hidden ? 'none' : null }}
                      onclick={evt => ws.editValue(evt.currentTarget,tw.input)}
                      // set data attributes
                      data-rowid={ row.id }
                      data-fieldname={ column.fieldname }
                      data-input={ column.input || "text" }
                    // set cell value
                    >{ row[column.fieldname] }</td> )}
                </For>  
              </tr>
            )}
          </For>
        </tbody>
      </table>
    </Suspense>
  )
}


// --- --- legacy code below --- --- //

// async function fetchData(): Promise<DataRow[]> {
  //   // fetch data from http REST API
  //   const params = new URLSearchParams(target)
  //   return await fetch(
  //     `http://localhost:8080/data?${params.toString()}`,
  //     {
  //       headers: { 
  //         "accept": "application/json",
  //         "sweetheart-action": "fetch.rest" }
  //     })
  //     .then(response => response.json())
  //     .then(json => json.Ok)
  // }