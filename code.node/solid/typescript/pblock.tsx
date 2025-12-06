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

type TypeValues = {
  id: string // e.g. In1, Out1, ...
  name: string
  values: [string, number|null][]
  valuation: [string, string][]
}

type TypeBlock = {
  name?: string
  measures: TypeMeasure[]
  computes: TypeMeasure[]
  payload: TypeValues[]
}

type TypeFlowSheet = {
  name?: string
  blocks: string[]
}

// Get TailwindCss classes
// const tw = new sweetheart.Style()
// document.body.className = tw.preset.body()


// Build Process Block Component
type ProcessBlockProps = {
  dataset: string,
  websocket: sweetheart.WebSocket
}

const ProcessBlock: Component<ProcessBlockProps> = (
  { dataset, websocket }): JSX.Element => {

  const [ data, setData ] = createResource(() => 
    websocket.fetch(dataset,"__block__") as Promise<TypeBlock>)

  return <ErrorBoundary fallback={(err) => <div> Error: { err.message } </div>}>
    <table class="text-xs my-2">
      <thead>
        <tr>
          <th class="w-12" />
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
        <For each={ data()?.payload ?? [] }>
          {(InOut: TypeValues) => (
            <tr class="text-center border-b border-collapse border-gray-200">
              <td class="text-left">{ InOut.id }</td>
              <For each={ data()?.measures ?? [] }>
                {(measure: TypeMeasure) => <>
                  <td
                    data-input="text"
                    data-set={ dataset }
                    data-rowid={ InOut.id }
                    data-fieldname={ measure.key }
                    onclick={(evt) => websocket.editValue(evt.currentTarget,
                      "scale-120 pl-1 w-16 bg-pink-50 focus:outline focus:outline-pink-400 rounded-xs")}
                  >{ new Map(InOut.values).get(measure.key) ?? "—" }</td>
                </>}
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
  </ErrorBoundary>
}


// Build Flow Sheet Component
export const FlowSheet = (
  { http, ws }: { http: string, ws: string }): JSX.Element => {

  const [ flow, setFlow ] = createResource(() => 
    sweetheart.GET(`${http}?origin=__flowsheet__`) as Promise<TypeFlowSheet>)

  const websocket = new sweetheart.WebSocket(ws,"__block__")
  return <Suspense fallback={<div> loading ... </div>}>

    <h1 class="text-xl">{ flow()?.name || "" }</h1>
    <hr />

    <For each={ flow()?.blocks ?? [] }>
      {(blockname: string) => 
        <ProcessBlock dataset={blockname} websocket={websocket}/> }
    </For>

  </Suspense>
}
