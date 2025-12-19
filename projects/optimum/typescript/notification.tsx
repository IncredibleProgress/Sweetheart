import "../resources/tailwind.css"
import { Style } from "./sweetheart"
import { render } from "solid-js/web"
import { JSX } from "solid-js/jsx-runtime"

const twcss = new Style()
document.body.className = twcss.preset.body()

// ---- ---- Main component rendering ---- ---- //

const Notification = (): JSX.Element => 
<div class="flex flex-col items-center h-screen justify-center">

<h1 class={twcss.preset.header()}>
    notification for maintenance </h1>

</div>
render(() => <Notification />, document.getElementById("app")!)