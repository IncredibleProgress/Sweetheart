import '../resources/tailwind.css'
import * as datasystem from './datasystem'
import { For, Suspense, createResource } from 'solid-js'


type DataRow = {
  id: number | string
  [key: string]: string | number | null
}

type TableColumn = {
  header: string
  fieldname: string
  input?: string
  class?: string
  hidden?: boolean
}

const columns: TableColumn[] =  [
  // { header: "Id", name: "id", hidden: true },
  { header: "Name", fieldname: "key", class: "w-32 p-1 text-center" },
  { header: "Value", fieldname: "value", class: "w-32 p-1 text-center" } ]


export const RtTable = () => {
  // Real-time Table Component

  const target = {table:"testtable"}
  const ws = new datasystem.WebSocket()

  const [ data ] = createResource(
    () => ws.fetch_table(target.table) as Promise<DataRow[]> )

  function onDataClick(elt: HTMLTableCellElement) {
    if (elt.querySelector("input")) {
      // input already exists
      return }
    else {
      // create input element
      const input = document.createElement("input")
      // 
      input.value = elt.innerText
      input.type = elt.dataset.input!
      // 
      input.oninput = () => {
        // update or insert data in real-time
        if (input.dataset.rowid !== "NEW") {
          ws.send_json({
            action: "ws.rest.PATCH",// update
            table: target.table,
            id: elt.dataset.rowid,
            name: elt.dataset.fieldname,
            value: input.value }) }
        else {
          ws.send_json({
            action: "ws.rest.POST",// insert
            table: target.table,
            row: {[elt.dataset.fieldname!]:input.value} }) }
      }
      input.onblur = () => {
        elt.innerText = input.value
        input.remove()
      }
      // set html input element
      elt.innerText = ""
      elt.appendChild(input)
      input.focus()
    }
  }

  return (
    <Suspense fallback={ <div class="m-2">loading...</div> }>
      <table>
        <thead>
          <tr class="font-semibold bg-slate-300">
            <For each={columns}>
              {(column: TableColumn) => (  
                <th>{ column.header }</th> )}
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
                      hidden={column.hidden}
                      // style={{ display: column.hidden ? 'none' : null }}
                      onclick={evt => onDataClick(evt.currentTarget)}
                      // set data attributes
                      data-rowid={row.id}
                      data-fieldname={column.fieldname}
                      data-input={ column.input || "text" }
                    // set cell value
                    > {row[column.fieldname]} </td> )}
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

// function fakeData() { return [
//     { id: 1, key: "one", value: 1 },
//     { id: 2, key: "two", value: 2 },
//     { id: 3, key: "three", value: 3 },
//     { id: 4, key: "four", value: 4 },
//     { id: 5, key: "five", value: 5 },
//     { id: 6, key: "six", value: 6 },
//     { id: 7, key: "seven", value: 7 } ]}

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