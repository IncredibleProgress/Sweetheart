import "../resources/tailwind.css"
import * as sweetheart from "./sweetheart"
import { JSX } from "solid-js/jsx-runtime"
import { For, Suspense, createResource } from 'solid-js'

const tw = new sweetheart.Style()
document.body.className = tw.preset.body()


export const ProcessBlock = (): JSX.Element => {

  const ws = new sweetheart.WebSocket()
  const [ data, setData ] = createResource(() => ws.fetchTable(table))

  return <Suspense fallback={<div> loading data... </div>}>
    <h1 class="text-2xl"> process unit </h1>
    <hr />

    <table class="mt-2 border-collapse border border-gray-400">
      <thead>
        <tr>
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
              <td class={ tw.data }>{ row["key"] }</td>
              <td class={ tw.data }>{ row["value"] }</td>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </Suspense>
}
