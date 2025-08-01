import { Style } from "./sweetheart"
import { render } from "solid-js/web"

const twcss = new Style()
document.body.className = twcss.preset.body()


// ---- ---- Main page ---- ---- //

const WelcomePage = () => 
<>
  <h1 class={ twcss.variant.biggerHeader() }>
    Sweetheart
  </h1>
  <h2 class={ twcss.variant.subTitle() }>
    innovative foundations for enterprise-grade solutions
  </h2>
</>

render(() => <Welcome />, document.getElementById("app")!)
