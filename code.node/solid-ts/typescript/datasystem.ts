// Sweetheart Data System API

// // set data types:
// export interface DataRow {
//   id: string | null
//   [field: string]: string | number | null
// }

// set websocket connection:
export class WebSocket extends window.WebSocket {

  constructor(url?: string) {

    if (!url) { url= "ws://localhost:8080/data" } // default
    super(url)

    this.onmessage = (ev) => { this.on_message(ev) }
    this.onopen = () => {console.log('WebSocket connection open')}
    this.onerror = () => {console.log('WebSocket connection error')}
    this.onclose = () => { alert('WebSocket connection closed') }
  }
  send_json(data: object) {
    // given for convenience
    super.send(JSON.stringify(data))
  }
  on_message(ev: MessageEvent) {
    const data = JSON.parse(ev.data)
    // ... do something with data
  }
}