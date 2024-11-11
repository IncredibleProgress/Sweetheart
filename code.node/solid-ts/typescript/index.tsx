import '../resources/tailwind.css'
import { render } from 'solid-js/web'
import { For, Show, createResource } from 'solid-js'

// create websocket connection:
const ws = new WebSocket("ws://localhost:8080/data")
ws.onopen = () => {console.log('WebSocket connection open')}
ws.onerror = () => {console.log('WebSocket connection error')}
ws.onclose = () => {console.log('WebSocket connection closed')}

// set data types:
interface Row {
  id: string
  [field: string]: string|number }

// set table fields headers:
let headers: string[] = []

// fetch initial data:
async function fetchInit(): Promise<Row[]> {
  const params = new URLSearchParams({
    table: "testtable",
  })
  const response = await fetch(`/data?${params.toString()}`,{
    headers: { 
      "sweetheart-action": "fetch.rest",
      "accept": "application/json",
    }
  })
  let json: Row[] = await response.json()
  if (json.length===0) { json = [
    {id:"", key:"", value:""}
  ]}
  return json
}

// set Solid-js component:
function Table() {

  const [data, { mutate, refetch }] = createResource<Row[]>(fetchInit)

  function fields(): string[] {
    if (headers.length===0) {
      const row = data()?.[0]; if (row) {
        headers = Object.keys(row).filter(key=>key!=='id') }
    }
    return headers
  }

  // build JSX <Table /> component:
  return(
    <div class="container mx-auto">
      <h1 class="text-4xl lg:text-6xl text-pink-500 italic my-4">
        Realtime Table </h1>

      <Show when={data.loading}>
        <div>loading...</div> </Show>

      <Show when={data.error}>
        <div>error: {data.error.message}</div> </Show>

      <Show when={data()}>
        {(data) => (
          <table class="table-auto border-collapse border">
            <thead>
              <tr>
                <For each={fields()}>
                  {(header) => (
                    <th class="border px-4 py-2 bg-gray-100">
                      {header}
                    </th>
                  )}
                </For>
              </tr>
            </thead>
            <tbody>
              <For each={data()}>
                {(row) => (
                  <tr id={row.id}>
                    <For each={fields()}>
                      {(name) => (
                        <td class="border px-4 py-2">
                          <input type="text" 
                            name={name} 
                            value={row[name]}
                            onBlur={(elt) => {
                              // update local state:
                              const value =
                                (elt.target as HTMLInputElement).value
                              // send update to server:
                              if (value && row.id==="") {
                                ws.send(JSON.stringify({
                                  // insert
                                  action: "ws.rest.post",
                                  table: "testtable",
                                  row: { [name]: value }
                                }))
                                refetch()//FIXME
                              } else if (value && row.id!=="") {
                                ws.send(JSON.stringify({
                                  // update 
                                  action: "ws.rest.patch",
                                  table: "testtable",
                                  id: row.id,
                                  field: name,
                                  value: value
                                }))
                              }
                            }}
                          />
                        </td>
                      )}    
                    </For>
                  </tr>
                )}
              </For>
            </tbody>
          </table>
        )}
      </Show>
    </div>
  )
}

// render app for testing:
render(() => <Table />,document.getElementById('webapp')!)


// --- --- Legacy code below --- ---

// // test connection to server:
// fetch("/data",{
//   headers: {"sweetheart-action":"fetch.test"}
// })
// .then(response => response.json())
// .then(data => { console.log(data) })