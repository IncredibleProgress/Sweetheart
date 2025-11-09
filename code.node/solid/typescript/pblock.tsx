import "../resources/tailwind.css"
import * as sweetheart from "./sweetheart"
import { JSX } from "solid-js/jsx-runtime"
import { For, Suspense, createResource } from 'solid-js'


// Set Data types
type TypeMeasure = {
  key: string;
  name: string;
  unit: string;
  type: number;
}
type TypeValues =
  Record<string, Record<string,number|null>[] >

type TypeBlock = {
  block: string;
  measures: TypeMeasure[];
  computes: TypeMeasure[];
  values: TypeValues[];
}


// Get TailwindCss classes
const tw = new sweetheart.Style()
document.body.className = tw.preset.body()


// Build Process Block Component
export const ProcessBlock = (): JSX.Element => {

  const ws = new sweetheart.WebSocket(
    "ws://localhost:8080/flowdata")

  const [ data, setData ] = createResource(
    () => ws.fetch("ExchangerBlock") as Promise<TypeBlock> )

  return <Suspense fallback={<div> loading data... </div>}>
    <h1 class="text-2xl"> Single Process Unit </h1>
    <hr />

    <table class="mt-2 border-collapse border border-gray-200">
      <thead>
        <tr>
          <th class=""> Name </th>
          <For each={ data()?.measures ?? [] }>
            {(measure: TypeMeasure) => (  
              <th class="">
                { measure.name } <br /> { measure.unit}
              </th>
            )}
          </For>
          <th class="w-4" />
          <For each={ data()?.computes ?? [] }>
            {(compute: TypeMeasure) => (  
              <th class="">
                { compute.name } <br /> { compute.unit }
              </th>
            )}
          </For>
        </tr>
      </thead>
      <tbody>
        <For each={ data()?.values ?? [] }>
          {(InOut: TypeValues, index) => (
            <tr>
              <td>{ Object.keys(InOut)[0] }</td>
              <For each={ data()?.measures ?? [] }>
                {(measure: TypeMeasure) => (  
                  <td
                    data-input = "text"
                    data-rowid = { Object.keys(InOut)[0] }
                    data-fieldname = { measure.key }
                  >{ Object.values(InOut)[0][index()][measure.key] ?? "—" }</td>
                )}
              </For>
              <th />
              <For each={ data()?.computes ?? [] }>
                {(compute: TypeMeasure) => (  
                  <td
                    data-rowid = { Object.keys(InOut)[0] }
                    data-fieldname = { compute.key }
                  >{ Object.values(InOut)[0][index()][compute.key] ?? "—" }</td>
                )}
              </For>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </Suspense>
}
