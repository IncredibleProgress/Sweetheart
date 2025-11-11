import "../resources/tailwind.css"
import { JSX } from "solid-js/jsx-runtime"
import * as sweetheart from "../resources/sweetheart"
import { For, Suspense, createResource } from 'solid-js'
import { className } from "solid-js/web"


// Set Data types
type TypeMeasure = {
  key: string
  name: string
  unit: string
  type: number
}

type TypeValues = {
  id: string // e.g. In1, Out1, ...
  values: [string,number|null][]
}

type TypeBlock = {
  block: string;
  measures: TypeMeasure[]
  computes: TypeMeasure[]
  values: TypeValues[]
}

// Get TailwindCss classes
const tw = new sweetheart.Style()
// document.body.className = tw.preset.body()


// Build Process Block Component
export const ProcessBlock = (): JSX.Element => {

  const ws = new sweetheart.WebSocket(
    "ws://localhost:8080/flowdata")

  const [ data, setData ] = createResource(
    () => ws.fetch("ExchangerBlock") as Promise<TypeBlock> )

  return <Suspense fallback={<div> Sweetheart is loading data ... </div>}>
    <h1 class="text-xl"> Single Process Unit </h1>
    <hr />

    <table class="text-xs mt-2">
      <thead>
        <tr>
          <th class="w-12" />
          <For each={ data()?.measures ?? [] }>
            {(measure: TypeMeasure) => (  
              <th class="w-16 font-light border-x border-collapse border-gray-200">
                { measure.name } <br /> { measure.unit}
              </th>
            )}
          </For>
          <th class="w-4" />
          <For each={ data()?.computes ?? [] }>
            {(compute: TypeMeasure) => (  
              <th class="w-16 font-light border-x border-collapse border-gray-200">
                { compute.name } <br /> { compute.unit }
              </th>
            )}
          </For>
        </tr>
      </thead>
      <tbody>
        <For each={ data()?.values ?? [] }>
          {(InOut: TypeValues) => (
            <tr class="text-center border-b border-collapse border-gray-200">
              <td class="text-left">{ InOut.id }</td>
              <For each={ data()?.measures ?? [] }>
                {(measure: TypeMeasure) => (  
                  <td
                    data-input="text"
                    data-rowid={ InOut.id }
                    data-fieldname={ measure.key }
                    onclick={(evt) => ws.editValue(evt.currentTarget,
                      "w-auto p-0.5 text-center focus:outline-2 focus:outline-pink-400")}
                  >{ new Map(InOut.values).get(measure.key) ?? "—" }</td>
                )}
              </For> 
              <th>*</th>
              <For each={ data()?.computes ?? [] }>
                {(compute: TypeMeasure) => (  
                  <td
                    data-rowid = { InOut.id }
                    data-fieldname = { compute.key }
                  >{ new Map(InOut.values).get(compute.key) ?? "—" }</td>
                )}
              </For>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </Suspense>
}
