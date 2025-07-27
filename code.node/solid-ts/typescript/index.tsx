import '../resources/tailwind.css'
import { render } from "solid-js/web"
// import { RtTable } from "./rtable"

// fetch("http://localhost:8080/data?table=testtable&database=test", {
// headers: { 
//     "Accept": "application/json",
//     "Sweetheart-Action": "fetch.test" }
// }).then(response => response.json())

const preset = {
  // TailwindCss style classes - presets
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

const twcss = (preset: Object, ...classes: string[]) => 
  [Object.values(preset).join(" "), ...classes].join(" ")

const variant = {
  // TailwindCss style classes - variants
  biggerHeader: twcss(preset.header,"lg:text-8xl")
}

const WelcomePage = () => 
<div class="">
  <h1 class={ variant.biggerHeader }>
    Sweetheart </h1>
  <h2>
    innovative foundations for enterprise-grade solutions </h2>
</div>

document.body.className = twcss(preset.body)
render(WelcomePage,document.getElementById("app")!)