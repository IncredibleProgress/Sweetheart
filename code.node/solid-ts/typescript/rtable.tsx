import '../resources/tailwind.css'
import * as datasystem from './datasystem'
import { For, Suspense, createResource } from 'solid-js'


type DataRow = {
  id: number | string
  [key: string]: string | number | null
}

type TableColumn = {
  title: string
  field: string
  class?: string
}

function fakeColumns() { return [
  { title: "Id", field: "id", hidden: true },
  { title: "Name", field: "key", class: "p-1 text-center" },
  { title: "Value", field: "value", class: "p-1 text-center" } ]}

function fakeData() { return [
    { id: 1, key: "one", value: 1 },
    { id: 2, key: "two", value: 2 },
    { id: 3, key: "three", value: 3 },
    { id: 4, key: "four", value: 4 },
    { id: 5, key: "five", value: 5 },
    { id: 6, key: "six", value: 6 },
    { id: 7, key: "seven", value: 7 } ]}


export const RtTable = () => {
  // Real-time Table Component

  const target = "test.testtable"
  const ws = new datasystem.WebSocket()

  async function fetchData(): Promise<DataRow[]> {
    // fetch data from http REST API
    const params = new URLSearchParams({
      database: target.split(".")?.[0],
      table: target.split(".")?.[1]
    })
    return await fetch(
      `http://localhost:8080/data?${params.toString()}`,
      {
        headers: { 
          "accept": "application/json",
          "sweetheart-action": "fetch.rest" }
      })
      .then(response => response.json())
      .then(json => json.Ok)
  }

  const columns = fakeColumns()
  // const [ data ] = createResource(fakeData)
  const [ data ] = createResource(fetchData)

  return (
    <Suspense fallback={ <div>loading...</div> }>
      <table>
        <thead>
          <tr class="font-semibold bg-slate-300">
            <For each={columns}>
              {(column: TableColumn) => (  
                <th data-field={column.field}>
                  { column.title } </th> )}
            </For>
          </tr>
        </thead>
        <tbody>
          <For each={data()}>
            {(row: DataRow) => (
              <tr>
                <For each={columns}>
                  {(column: TableColumn) => (
                    <td
                      class={column.class}
                      data-rowid={row.id}
                      data-field={column.field}
                      onclick={evt => console.log(evt.target)}
                    > { row[column.field] } </td> )}
                </For>  
              </tr>
            )}
          </For>
        </tbody>
      </table>
    </Suspense>
  )
}
