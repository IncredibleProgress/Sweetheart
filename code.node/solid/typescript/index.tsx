// Import solid-js facilities
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"

// Import routed components
import { ProcessBlock } from "./pblock"
import { Welcome } from "../resources/components"

// Render components based on URL path
const Router = (): JSX.Element =>  {
  switch(window.location.pathname) {

    case "/flow": 
      return <ProcessBlock />

    default:
      return <Welcome />
  }
}
render(() => <Router />, document.getElementById("app")!)
