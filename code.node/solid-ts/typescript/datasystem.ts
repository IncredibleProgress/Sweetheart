// Sweetheart Data System API

// set websocket connection:
export class WebSocket extends window.WebSocket {

  constructor(url?: string) {

    if (!url) { url= "ws://localhost:8080/data" } // default
    super(url)

    // this.onmessage must be implemented by the user
    this.onopen = () => {console.log("WebSocket connection open.")}
    this.onerror = () => {console.log("WebSocket connection error.")}
    this.onclose = () => {console.log("WebSocket connection closed.")}
  }
  send_json(data: object) {
    // given for convenience
    super.send(JSON.stringify(data))
  }
  send_bjson(data: object) {
    // given for convenience
    const json = JSON.stringify(data)
    const bytes = new TextEncoder().encode(json)
    super.send(bytes)
  }
  waitForConnection() {
    return new Promise((resolve, reject) => {
      if (this.readyState === this.OPEN) { resolve(true) }
      else {
        this.addEventListener("open",()=>{ resolve(true) },{once:true})
        this.addEventListener("error",()=>{ reject(false) },{once:true})
      } })
  }
  fetch_table(table: string) {
    return new Promise((resolve, reject) => {

      const timeoutId = setTimeout(() => { reject(
        "Timeout exceeded in WebSocket.fetch_table()") }, 1000)

      const request_uuid = crypto.randomUUID()
      const messageHandler = (evt: MessageEvent) => {
        const data = JSON.parse(evt.data)
        if (data.uuid === request_uuid) {
          clearTimeout(timeoutId)
          this.removeEventListener("message",messageHandler)
          if (data.Ok) { resolve(data.Ok) }
          else { reject(data.Err) } }}

      this.waitForConnection()
        .then(() => {
          this.addEventListener("message",messageHandler)
          this.send_json({
            uuid: request_uuid,
            action: "ws.rest.GET",
            table: table }) })
        .catch((err) => { 
          clearTimeout(timeoutId)
          reject(err) })
    })
  }
}