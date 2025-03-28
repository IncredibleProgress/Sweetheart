// Sweetheart Data System API

// set websocket connection:
export class WebSocket extends window.WebSocket {

  connectDB: { 
    database?: string,
    table: string | undefined,
    user?: string, //FIXME
    password?: string, //FIXME
  }

  constructor(url?: string, db?: string) {

    url= url || "ws://localhost:8080/data"
    super(url,"json") // set json sub-protocol

    this.connectDB = {
      database: db || "test", // default
      table: undefined, }

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
  fetchTable(table: string) {
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
          this.connectDB.table = table
          this.addEventListener("message",messageHandler)
          this.send_json({
            uuid: request_uuid,
            action: "ws.rest.get",
            table: this.connectDB.table,
            database: this.connectDB.database }) })
        .catch((err) => { 
          clearTimeout(timeoutId)
          reject(err) })
    })
  }
  editValue(elt: HTMLTableCellElement, className?: string) {
    if (elt.querySelector("input")) {
      // input already exists, do nothing
      return }
    else {
      // create input element, for editing
      const input = document.createElement("input")
      // 
      input.value = elt.innerText
      input.type = elt.dataset.input!
      input.className = className || ""
      // 
      input.oninput = () => {
        // update or insert data in real-time
        if (input.dataset.rowid == "TO INSERT") {
          this.send_json({
            action: "ws.rest.post",// insert
            table: this.connectDB.table,
            row: {[elt.dataset.fieldname!]:input.value} }) }
        else {
          this.send_json({
            action: "ws.rest.patch",// update
            table: this.connectDB.table,
            id: elt.dataset.rowid,
            name: elt.dataset.fieldname,
            value: input.value }) }
      }
      input.onblur = () => {
        elt.innerText = input.value
        input.remove()
      }
      // set html input element
      elt.innerText = ""
      elt.appendChild(input)
      input.focus()
    }
  }
}