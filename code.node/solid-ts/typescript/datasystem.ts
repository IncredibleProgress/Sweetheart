// Sweetheart Data System API

import { Accessor } from "solid-js"

// settings:
const DATA_SOURCE = "http://localhost:8080/data"

// set data types:
interface DataRow {
    id: string
    [field: string]: string | number
  }
  
  // handle table data:
  export class DataHub {
  
    // websocket connection
    ws: WebSocket
    // database settings
    system: string = "RethinkDB"
    database: string = "test" //! default
    curtable?: string = undefined
    // table settings
    columns: Record<string,string>[] = []
    default: DataRow = {id:"", key:"", value:""}
  
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
    getHeaders(data: Accessor<DataRow[]>): string[] {

      if (this.columns.length===0) {
        // autoset headers from 1st data row
        const row = data()?.[0]
        if (row) {
          this.columns = Object.keys(row).map(key => ({
            name: key,
            header: key }))
      }}
      return this.columns.map(col => col.header)
    }
    insert(elt: HTMLInputElement) {
  
      const tr = elt.closest('tr')
      const record: Record<string,string|number> = {}
  
      this.ws.send(JSON.stringify({
        // head
        action: "ws.rest.post",
        target: `${this.database}.${this.curtable}`,
        // body
        insert: this.columns.reduce((acc,column) => {
          const name = CSS.escape(column.name)
          const input = tr?.querySelector(`input[name=${name}]`) as HTMLInputElement
          if (!input) { throw "TypeError: HTMLInputElement expected" }
          acc[input.name] = input.value 
          return acc }, record)
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
        patch: elt.name,
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
  }