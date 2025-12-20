import "../resources/tailwind.css"
import { JSX } from "solid-js/jsx-runtime"
import * as sweetheart from "../resources/sweetheart"
import { ErrorBoundary, For, Suspense, createResource, Component } from 'solid-js'


// Set Data types
type TypeMeasure = {
  key: string
  name: string
  unit: string
  type: number
}

type TypeInOut = {
  key: string
  name: string
}

type TypeBlock = {
  blockname?: string
  measures: TypeMeasure[]
  computes: TypeMeasure[]
  inouts: TypeInOut[]
  payload: [ string, number|null ][]
  // `${inout.key}.${measure.key}` => value
}

// Build Process Block Component
type ProcessBlockProps = {
  dataset: string,
  websocket: sweetheart.WebSocket
}

const ProcessBlock: Component<ProcessBlockProps> = (
  { dataset, websocket }): JSX.Element => {

  const [ data ] = createResource(() => 
    websocket.fetch(dataset,"__block__") as Promise<TypeBlock>)

  const payload = () => new Map(data()?.payload)

  function updateValue(
      element: HTMLTableCellElement,
      className?: string) {

    websocket.editValue(element, className)
  }

  return <ErrorBoundary fallback={(err) => <div> Error: { err.message } </div>}>
    <table class="text-xs my-2">
      <thead>
        <tr>
          <th class="w-32" />
          <For each={ data()?.measures ?? [] }>
            {(measure: TypeMeasure) => <>
              <th class="w-16 font-light border-x border-collapse border-gray-200">
                { measure.name } <br /> { measure.unit}
              </th>
            </>}
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
        <For each={ data()?.inouts ?? [] }>
          {(InOut: TypeInOut) => (
            <tr class="text-center border-b border-collapse border-gray-200">
              <td class="text-left">{ InOut.name }</td>
              <For each={ data()?.measures ?? [] }>
                {(measure: TypeMeasure) => <>
                  <td
                    data-input="number"
                    data-set={ dataset }
                    data-id={ InOut.key }
                    data-key={ measure.key }
                    onclick={(evt) => updateValue(evt.currentTarget,
                      "scale-110 pl-1 w-16 bg-pink-50 focus:outline focus:outline-pink-400 rounded-xs"
                    )}
                  >{ payload().get(`${InOut.key}::${measure.key}`) || "—" }</td>
                </>}
              </For> 
              <th>*</th>
              <For each={ data()?.computes ?? [] }>
                {(compute: TypeMeasure) => (  
                  <td
                    data-id = { InOut.key }
                    data-key = { compute.key }
                  >{ payload().get(`${InOut.key}::${compute.key}`) || "—" }</td>
                )}
              </For>
            </tr>
          )}
        </For>
      </tbody>
    </table>
  </ErrorBoundary>
}

// Build Flow Sheet Component

type TypeFlowSheet = {
  flowsheet?: string
  blocks: string[]
}

export const FlowSheet = (
  { http, ws }: { http: string, ws: string }): JSX.Element => {

  const [ flow ] = createResource(() => 
    sweetheart.GET(`${http}?origin=__flowsheet__`) as Promise<TypeFlowSheet>)

  const websocket = new sweetheart.WebSocket(ws,"__block__")
  return <Suspense fallback={<div> loading ... </div>}>

    <h1 class="text-xl">{ flow()?.flowsheet || "" }</h1>
    <hr />

    <For each={ flow()?.blocks ?? [] }>
      {(blockname: string) => 
        <ProcessBlock dataset={blockname} websocket={websocket}/> }
    </For>

  </Suspense>
}
