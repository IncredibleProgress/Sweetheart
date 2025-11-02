import "../resources/tailwind.css"
import * as sweetheart from "./sweetheart"
import { JSX } from "solid-js/jsx-runtime"
import { For, Suspense, createResource } from 'solid-js'


// Get TailwindCss classes
const tw = new sweetheart.Style()
document.body.className = tw.preset.body()


// Set Data types
type TypeMeasure = {
  name: string;
  unit: string;
  type: number;
}
type TypeBlock = {
  block: string;
  measures: TypeMeasure[];
  computes: TypeMeasure[];
  values: Record<string,Record<string,number|null>>;
}


// Build Process Block Component
export const ProcessBlock = (): JSX.Element => {

  const ws = new sweetheart.WebSocket()

  const [ data, setData ] = createResource(
    () => ws.fetchTable("ExchangerBlock") as Promise<TypeBlock> )

  return <Suspense fallback={<div> loading data... </div>}>
    <h1 class="text-2xl"> Single Process Unit </h1>
    <hr />

    <table class="mt-2 border-collapse border border-gray-200">
      <thead>
        <tr>
          <th class={ tw.preset.header() }> Name </th>
          <For each={ data()?.measures ?? [] }>
            {(measure: TypeMeasure) => (  
              <th class={ tw.preset.header() }>
                { measure.name } <br /> { measure.unit}
              </th>
            )}
          </For>
          <For each={ data()?.computes ?? [] }>
            {(compute: TypeMeasure) => (  
              <th class={ tw.preset.header() }>
                { compute.name } <br /> { compute.unit }
              </th>
            )}
          </For>
        </tr>
      </thead>
      <tbody>
        <For each={ Object.entries(data()?.values ?? {}) }>
          {([name, inout]: [string, Record<string,number|null>]) => (
            <tr>
              <td class="">{ name }</td>
              <td class="">
                <For each={ Object.entries(inout) }>
                  {([k, v]) => <span>{k}: {v ?? "—"} </span>}
                </For>
              </td>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </Suspense>
}
