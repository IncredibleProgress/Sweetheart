// import * as svg from "./svg"
import "../resources/tailwind.css"
import { Style } from "./sweetheart"
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"


// ---- ---- Tailwind CSS Setup ---- ---- //

const tw = new Style()
document.body.className = tw.preset.body()


// ---- ---- Default Component ---- ---- //

const Welcome = (): JSX.Element => 
  <div class="flex flex-col items-center h-screen justify-center text-center">

    <h1 class={ tw.variant.biggerHeader() }>
      Sweetheart </h1>

    <h2 class={ tw.variant.biggerSubtitle() }>
      innovative foundations for business-grade solutions </h2>

  <br /> 

    <h3 class={ tw.preset.highlight() }>
      <span class="text-3xl">0</span>
        % distraction | waste of time </h3>

    <h3 class={ tw.preset.highlight() } >
      <span class="text-3xl">100</span>
        % focus on business results </h3>
    
  <br />

    <p class={ tw.preset.subtitle() }>
      feel you ready ? </p>

    <button class={ tw.preset.button() }>
      start now </button>

  <br />
  <br />

    <p class="text-gray-300 text-sm">
      by Nicolas Champion, Sweetheart's maker </p>

  </div>


// ---- ---- Main component rendering ---- ---- //

const WebApp = (): JSX.Element =>  {
  switch(window.location.pathname) {

    // case "/welcome": 
    //   return(<WelcomePage/>)

    default:
      return <Welcome />
  }
}
render(() => <WebApp />, document.getElementById("app")!)