// Import solid-js facilities
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"

// Import routed components and styles
import { FlowSheet } from "./pblock"
import { Welcome } from "../resources/components"
import { Style } from "../resources/sweetheart"

// Tailwind CSS Setup 
const tailwind = new Style()
document.body.className = tailwind.preset.body()

// Render components based on URL path
const Router = (): JSX.Element =>  {
  switch(window.location.pathname) {

    case "/flow": 
      return <FlowSheet http="http://localhost:8080/flowdata" ws="ws://localhost:8080/flowdata" />

    default:
      return <Welcome style={tailwind} />
  }
}
render(() => <Router />, document.getElementById("app")!)
