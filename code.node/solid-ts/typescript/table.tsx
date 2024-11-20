import '../resources/tailwind.css'
import { DataRow, useDataHub } from './datasystem'
import { For, Show, createResource } from 'solid-js'


export const Table = () => {

  const [ dhub, init ] = useDataHub("testtable")
  const [ data, { mutate, refetch } ] = createResource<DataRow[]>(init)

  // set fields dynamically from data:
  const fields = () => dhub.getHeaders(data())

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
                            oninput={(elt) => {
                              dhub.handleChange(row.id,elt.target)
                              if (!row.id) { refetch() }
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