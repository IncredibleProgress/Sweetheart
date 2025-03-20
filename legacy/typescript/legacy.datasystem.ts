// Sweetheart Data System API

// global settings:
const DATA_SOURCE = "http://127.0.0.1:8080/data"

// set data types:
export interface DataRow {
    id: string | undefined
    [field: string]: string | number | undefined
  }


class DataHub {

  // websocket connection
  ws: WebSocket
  // database settings
  system: string = "RethinkDB"
  database: string = "test" //! default
  curtable?: string = undefined
  // table settings
  columns: Record<string,string>[] = []
  default: DataRow = {id:undefined, key:"", value:""}

  constructor(
      table: string, 
      database?: string ) {

    // set target at server side
    this.curtable = table
    if (database) { this.database = database }

    // create websocket connection:
    this.ws = new WebSocket(DATA_SOURCE)
    this.ws.onopen = () => {console.log('WebSocket connection open')}
    this.ws.onerror = () => {console.log('WebSocket connection error')}
    this.ws.onclose = () => {console.log('WebSocket connection closed')}
  }
  newTarget(
      table: string, 
      database?: string ) {

    // reset target at server side
    this.curtable = table
    if (database) { this.database = database }
  }
  async fetchInit(): Promise<DataRow[]> {

    if (!this.curtable) { 
      throw "ValueError: 'table' attribute expected"
    }
    const params = new URLSearchParams({
      system: this.system,
      database: this.database,
      table: this.curtable
    })
    const url = `${DATA_SOURCE}?${params.toString()}`
    const response = await fetch(url, {
      headers: { 
        "accept": "application/json",
        "sweetheart-action": "fetch.rest" }
    })
    let json: DataRow[] = await response.json()
    if (json.length===0) { json=[this.default] }
    return json
  }
  setColumns(data: DataRow[] | undefined) {

    if (this.columns.length===0) {
      // autoset headers from 1st data row
      const row: DataRow | undefined = data?.[0]
      if (row) {
        this.columns = Object.keys(row)
          //NOTE: filter out 'id' column
          .filter(key => key !== "id")
          .map(key => ({
            title: key,
            field: key,
            editor: "input" }))
    }}
    // return this.columns.map(col => col.title)
    return this.columns
  }
  insert(elt: HTMLInputElement) {

    const tr = elt.closest('tr')
    const init: Record<string,string|number> = {}

    this.ws.send(JSON.stringify({
      // head
      action: "ws.rest.post",
      target: `${this.database}.${this.curtable}`,
      // body
      insert: this.columns.reduce((result,column) => {
        const name = CSS.escape(column.name)
        const input = tr?.querySelector(`input[name=${name}]`) as HTMLInputElement
        if (!input) { throw "TypeError: HTMLInputElement expected" }
        if (input.name !== "id") {result[input.name] = input.value }
        return result }, init)
    }))
  }
  update(elt: HTMLInputElement) {

    const rowid = elt.closest('tr')?.id
    if (!rowid) { throw "ValueError: 'id' attribute expected" }

    this.ws.send(JSON.stringify({
      // head
      action: "ws.rest.patch",
      target: `${this.database}.${this.curtable}`,
      // body
      id: rowid,
      name: elt.name,
      value: elt.value
    }))
  }
  delete(elt: HTMLInputElement) {

    const rowid = elt.closest('tr')?.id
    if (!rowid) { throw "ValueError: 'id' attribute expected" }
    
    this.ws.send(JSON.stringify({
      // head
      action: "ws.rest.delete",
      target: `${this.database}.${this.curtable}`,
      // body
      id: rowid
    }))
  }
  handleChange(
      id: string | undefined, 
      elt: HTMLInputElement ) {

    if (elt.value && !id) { this.insert(elt) }
    else if (elt.value && id) { this.update(elt) }
  }
}


// convenient function to use DataHub
export function useDataHub(
    table: string, 
    database?: string ): 
      [DataHub,() => Promise<DataRow[]>] {

  const hub = new DataHub(table,database)
  const load = hub.fetchInit.bind(hub)

  return [ hub, load ]
}