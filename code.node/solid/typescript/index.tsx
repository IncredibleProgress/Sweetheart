// Import solid-js facilities
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"

// Import routed components and styles
import { ProcessBlock } from "./pblock"
import { Welcome } from "../resources/components"
import { Style } from "../resources/sweetheart"

// Tailwind CSS Setup 
const tailwind = new Style()
document.body.className = tailwind.preset.body()

// Render components based on URL path
const Router = (): JSX.Element =>  {
  switch(window.location.pathname) {

    case "/flow": 
      return <ProcessBlock />

    default:
      return <Welcome tw={tailwind} />
  }
}
render(() => <Router />, document.getElementById("app")!)
