import '../resources/tailwind.css'
import { render } from "solid-js/web"


class Style {
  // Interface for TailwindCss style classes

  presetValues = {
    body: {
      color: "bg-gray-50",
      spacing: "max-w-screen-lg mx-auto"
    },
    header:  {
      font: "text-5xl italic",
      color: "text-pink-500",
      spacing: "my-6"
    }
  }

  variantValues = {
    biggerHeader: [ this.presetValues.header, "lg:text-8xl" ]
  }

  className (preset: Object, ...classes: string[]): string {
    return [...Object.values(preset), ...classes].join(" ") as string;
  }
  
  preset: Record<string, () => string> = {};
  variant: Record<string, () => string> = {};

  constructor () {
    Object.entries(this.presetValues).forEach(([key, value]) => {
      this.preset[key as keyof typeof this.presetValues] = () => this.className(value);
    })
    Object.entries(this.variantValues).forEach(([key, value]) => {
      this.variant[key as keyof typeof this.variantValues] = () => 
        this.className(...value as [Object, ...string[]]);
    })
  }
}


const twcss = new Style()
document.body.className = twcss.preset.body()

const WelcomePage = () => 
<div class="">
  <h1 class={ twcss.variant.biggerHeader() }>
    Sweetheart </h1>
  <h2>
    innovative foundations for enterprise-grade solutions </h2>
</div>

render(()=> WelcomePage(), document.getElementById("app")!)


// ---- ---- Legacy code ---- ---- //

// import { RtTable } from "./rtable"

// fetch("http://localhost:8080/data?table=testtable&database=test", {
// headers: { 
//     "Accept": "application/json",
//     "Sweetheart-Action": "fetch.test" }
// }).then(response => response.json())