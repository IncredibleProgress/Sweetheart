import { render } from "solid-js/web"
import { RtTable } from "./rtable"

// fetch("http://localhost:8080/data?table=testtable&database=test", {
// headers: { 
//     "Accept": "application/json",
//     "Sweetheart-Action": "fetch.test" }
// }).then(response => response.json())

// render app for testing:
// const TestApp = () => <><br/><h1>Test App</h1></>

// render webapp:
// render(RtTable, document.body)
render(RtTable, document.getElementById("webapp")!)
