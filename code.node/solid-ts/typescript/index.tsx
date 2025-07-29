import '../resources/tailwind.css'
import { render } from "solid-js/web"


// ---- ---- TailwindCss style classes ---- ---- //

type TwClasses = Record<string, string>
type TwVariant = [ TwClasses, ...string[] ]

class Style {

  presetValues: Record<string, TwClasses> = {
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

  variantValues: Record<string, TwVariant> = {
    biggerHeader: [ this.presetValues.header, "lg:text-8xl" ]
  }
  
  preset: Record<string, () => string> = {};
  variant: Record<string, () => string> = {};

  className(...classes: TwVariant): string {
    return [...Object.values(classes[0]), ...classes.slice(1)].join(" ");
  }

  constructor() {

    Object.entries(this.presetValues).forEach(([key, value]) => {
      this.preset[key as keyof typeof this.presetValues] = () => this.className(value);
    })

    Object.entries(this.variantValues).forEach(([key, value]) => {
      this.variant[key as keyof typeof this.variantValues] = () => this.className(...value);
    })
  }
}

const twcss = new Style()
document.body.className = twcss.preset.body()


// ---- ---- Main page ---- ---- //

const WelcomePage = () => 
<>
  <h1 class={ twcss.variant.biggerHeader() }>
    Sweetheart </h1>
  <h2>
    innovative foundations for enterprise-grade solutions </h2>
</>

render(() => <WelcomePage />, document.getElementById("app")!)


// ---- ---- Legacy code ---- ---- //

// import { RtTable } from "./rtable"

// fetch("http://localhost:8080/data?table=testtable&database=test", {
// headers: { 
//     "Accept": "application/json",
//     "Sweetheart-Action": "fetch.test" }
// }).then(response => response.json())