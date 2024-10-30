import '../resources/tailwind.css'
import { render } from 'solid-js/web'

function App() {

  fetch("/data",{
    method: "GET",
    headers: {"Sweetheart-Action":"fetch.test"} })
  .then(response => response.json())
  .then(data => { console.log(data) })

  return(
    <div class="my-28">

      <h1 class="text-4xl lg:text-6xl text-pink-500 text-center italic">
        Welcome to Sweetheart </h1>

      <p class="text-center mt-4">
        get at {window.location.pathname} </p>
    </div>
  )
}

render(App,document.getElementById('webapp')!)