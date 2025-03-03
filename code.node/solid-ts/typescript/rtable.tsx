import '../resources/tailwind.css'
import * as datasystem from './datasystem'
import { For, Suspense, createResource } from 'solid-js'

export const defaultColumns = [
  { title: "Id", field: "id", hidden: true },
  { title: "Name", field: "key", class: "p-1 text-center", editor: "input" },
  { title: "Value", field: "value", class: "p-1 text-center", editor: "input" },
]

const TextInputEditor = (props) => {
  // Input Editor Component
  return (
    <input type="text"
      value={props.value} />
  )
}

export const RtTable = (columns, target, tableId=null) => {
  // Real-time Table Component

  columns = columns || defaultColumns
  target = target || "test.testtable"

  const ws = new datasystem.WebSocket()
  const [ data ] = createResource(fetchData)

  async function fetchData(): Promise<datasystem.DataRow[]> {
    // allow fetching data from http REST API
    const params = new URLSearchParams({
      database: target.split(".")?.[0],
      table: target.split(".")?.[1]
    })
    return await fetch(
      `${datasystem.source("http")}?${params.toString()}`,
      {
        headers: { 
          "accept": "application/json",
          "sweetheart-action": "fetch.rest" }
      }
    ).then(response => response.json())
  }

  function cellEditor(target,rowid,column): void {
    target.innerHTML = `<TextInputEditor value=${target.value} />`
  }

  return (
    <Suspense fallback={ <div>loading...</div> }>
      <table>
        <thead>
          <tr class="font-semibold bg-slate-300">
            <For each={columns}>
              {(column) => (  
                <th data-field={column.field}>
                  { column.title } </th> )}
            </For>
          </tr>
        </thead>
        <tbody>
          <For each={data()}>
            {(row) => (
              <tr>
                <For each={columns}>
                  {(column) => (
                    <td
                      class={column.class}
                      data-rowid={row.id}
                      data-field={column.field}
                      onclick={evt => cellEditor(evt.target,row.id,column)}
                    > {row[column.field]} </td> )}
                </For>  
              </tr>
            )}
          </For>
        </tbody>
      </table>
    </Suspense>
  )
}
