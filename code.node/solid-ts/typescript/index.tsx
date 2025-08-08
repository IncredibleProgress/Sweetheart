// import * as svg from "./svg"
import "../resources/tailwind.css"
import { Style } from "./sweetheart"
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"

const twcss = new Style()
document.body.className = twcss.preset.body()

// ---- ---- Main component rendering ---- ---- //

const Welcome = (): JSX.Element => 
<div class="flex flex-col items-center h-screen justify-center text-center">

  <h1 class={ twcss.variant.biggerHeader() }>
    Sweetheart </h1>

  <h2 class={ twcss.variant.biggerSubtitle() }>
    innovative foundations for enterprise-grade solutions </h2>

<br /> 

  <h3 class={ twcss.preset.highlight()  }>
    <span class="text-3xl">0</span>
      % distraction | waste of time </h3>

  <h3 class={ twcss.preset.highlight() } >
    <span class="text-3xl">100</span>
      % focus on business results </h3>
  
<br />

  <p class={ twcss.preset.subtitle() }>
    feel you ready ? </p>

  <button class={ twcss.preset.button() }>
    start now </button>

<br />

  <p class="text-gray-300 text-sm">
    by Nicolas Champion, sweetheart maker for a better life </p>

</div>
render(() => <Welcome />, document.getElementById("app")!)