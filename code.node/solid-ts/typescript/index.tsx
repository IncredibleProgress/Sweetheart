import '../resources/tailwind.css'
import { render } from 'solid-js/web'
import { For, Show, createResource } from 'solid-js'

// create websocket connection:

const ws = new WebSocket("ws://localhost:8080/data")
ws.onopen = () => {console.log('WebSocket connection open')}
ws.onerror = () => {console.log('WebSocket connection error')}
ws.onclose = () => {console.log('WebSocket connection closed')}

// test connection to server:

fetch("/data",{
  headers: {"sweetheart-action":"fetch.test"}
})
.then(response => response.json())
.then(data => { console.log(data) })

// set data types:

interface Row {
  id: string
  [field: string]: string | number }

// fetch initial data:

async function fetchInit(): Promise<Row[]> {
  const params = new URLSearchParams({table: "testtable"})
  const response = await fetch(`/data?${params.toString()}`,{
    headers: { 
      "sweetheart-action": "fetch.rest",
      "accept": "application/json",
    }
  })
  return await response.json()
}

// set main component:

function Table() {

  const [data, { mutate }] = createResource<Row[]>(fetchInit)
  
  return(
    <div>
      <h1 class="text-4xl lg:text-6xl text-pink-500 italic my-4">
        realtime table </h1>

      <Show when={data.loading}>
        <div>loading...</div> </Show>

      <Show when={data.error}>
        <div>error: {data.error.message}</div> </Show>

      <Show when={!data.loading && !data.error}>
        {(data) => (
          <table class="table-auto mx-auto border-collapse border">
            <thead>
              <tr>
                <For each={Object.keys(data()[0])}>
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
                    <For each={Object.keys(data()[0])}>
                      {(name) => (
                        <td class="border px-4 py-2">
                          <input type="text" name={name} value={row[name]} />
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

// render app:
render(() => <Table />,document.getElementById('webapp')!)