import '../resources/tailwind.css'
import { render } from "solid-js/web"
// import { RtTable } from "./rtable"

// fetch("http://localhost:8080/data?table=testtable&database=test", {
// headers: { 
//     "Accept": "application/json",
//     "Sweetheart-Action": "fetch.test" }
// }).then(response => response.json())

const style = {
  // TailwindCss style classes
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

function twcss(
  classes: Record<string, string>,
  variant?: string ): string
{ return Object.values(classes).join(" ")+` ${variant}` }

const WelcomePage = () => 
<div class="">
  <h1 class={twcss(style.header,"lg:text-8xl")}>
    Sweetheart </h1>
  <h2>
    innovative foundations for enterprise-grade solutions </h2>
</div>

document.body.className = twcss(style.body)
render(WelcomePage,document.getElementById("app")!)