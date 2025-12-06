/** This file is a part of Sweetheart project. */

/////////////////////////////////////////////
//  TailwindCss Style Classes  /////////////
///////////////////////////////////////////

export type TwClasses = Record<string, string>
type TwVariant = { preset?: TwClasses, chain?: string, omit?: string }

export class Style {

  // Define base style classes.
  // see https://play.tailwindcss.com
  public presetValues: Record<string, TwClasses> = 
    {
      body: {
        color: "bg-gray-50",
        spacing: "max-w-screen-lg mx-auto"
      },
      header:  {
        font: "text-5xl italic",
        color: "text-pink-500",
        spacing: "mt-4 mb-2"
      },
      subtitle: {
        font: "text-xl italic",
        color: "text-gray-500",
        spacing: "my-2"
      },
      highlight: {
        font: "text-lg",
        color: "text-pink-500",
        spacing: "my-2"
      },
      button: {
        font: "text-lg",
        color: "text-white bg-pink-500 hover:bg-pink-600",
        spacing: "m-4 px-4 py-2",
        shape: "rounded-sm"
      },
    }

  // Define customized style classes.
  // see https://play.tailwindcss.com
  public variantValues: Record<string, TwVariant> = 
    {
      biggerHeader: { 
        preset: this.presetValues.header,
        chain: "lg:text-8xl"
      },
      biggerSubtitle: {
        preset: this.presetValues.subtitle,
        chain: "lg:text-2xl",
      }
    }
  
  // Set namespaces for style classes.
  preset: Record<string, () => string> = {};
  variant: Record<string, () => string> = {};

  /**
   * Generate a string of unique classes based on the given variant.
   * @param variant An object containing preset, chain, and omit properties.
   * @returns A string of unique class names.
   */
  className({...variant}: TwVariant): string 
  {
    // Create a Set for holding unique classes
    const classSet = new Set<string>()

    // Add classes given by preset to classSet.
    if (variant.preset) {
      Object.values(variant.preset).forEach(classGroup => {
        classGroup.split(/\s+/).forEach(cls => {
          if (cls.length > 0) classSet.add(cls);
        })
      })
    }
    // Add classes given by chain to classSet.
    if (variant.chain) {
      variant.chain.split(/\s+/).forEach(cls => {
        if (cls.length > 0) classSet.add(cls);
      })
    }
    // Suppress classes given by omit from classSet.
    if (variant.omit) {
      variant.omit.split(/\s+/).forEach(omitClass => {
        if (omitClass.length > 0) classSet.delete(omitClass);
      })
    }
    // Return unique classes of classSet as a string.
    return Array.from(classSet).join(" ");
  }

  constructor()
  {
    Object.entries(this.presetValues).forEach(([key, value]) => {
      this.preset[key as keyof typeof this.presetValues] = 
        () => this.className({ preset: value }) + " "; 
        /* 
          Space at end allows chaining classes as follow:

            const twcss = new Style()
            className = { twcss.preset.body() + "text-center" }
        */
    })
    Object.entries(this.variantValues).forEach(([key, value]) => {
      this.variant[key as keyof typeof this.variantValues] = 
        () => this.className(value) + " ";
    })
  }
}


/////////////////////////////////////////////
//  Sweetheart Data System API  ////////////
///////////////////////////////////////////

// Default JSON type used for data exchange.
type json = Record<string,any>

// Http GET function for fetching data.
export function GET(urlquery: string): Promise<json> {
  return fetch(urlquery, { method: "GET",
    headers: {
      "accept": "application/json",
      "sweetheart-action": "fetch.rest"
    }
  })
  .then(response => {
    if (!response.ok) { throw new Error(
      `HTTP Error ${response.status}: ${response.statusText}`
    )}
    return response.json();
  })
  .then(json => { 
    if (json.Err) { throw new Error(
      `Error running ASGI Python app: ${json.Err}`
    )} 
    return json.Ok;
  })
  .catch(err => { throw new Error(
    `Error fetching data: ${err.message}`
  )})
}

// WebSocket class for real-time data connection.
export class WebSocket extends window.WebSocket {

  endpoint: {
    // data connection settings
    // info: string | undefined
    url: string
    origin: string | undefined // e.g. default database name
    dataset: string | undefined // e.g. default table name
    //FIXME login: string | undefined
    //FIXME getpass: string | undefined
  }

  constructor(
      url: string,
      origin?: string,
      dataset?: string ) {

    // set json sub-protocol
    super(url,"json")

    // set data connection settings
    this.endpoint = {
      url: url,
      origin: origin || "test",// e.g. database name
      dataset: dataset || undefined,// e.g. table name
    }

    //NOTE: this.onmessage must be implemented by the user
    this.onopen = () => console.log("WebSocket connection open.");
    this.onerror = () => {throw new Error("WebSocket connection error.")};
    this.onclose = () => console.log("WebSocket connection closed.");
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
      if (this.readyState === this.OPEN) resolve(true);
      else {
        this.addEventListener("open",()=> resolve(true), {once:true})
        this.addEventListener("error",()=> reject(false), {once:true})
      } })
  }

  fetch(dataset?: string, origin?: string) {
    return new Promise((resolve, reject) => {
      
      const request_uuid = crypto.randomUUID()
      const timeoutId = setTimeout(() => { reject(
        "Timeout exceeded in WebSocket.fetchTable()") }, 1000)

      const messageHandler = (evt: MessageEvent) => {
        const data = JSON.parse(evt.data)
        if (data.uuid === request_uuid) {
          clearTimeout(timeoutId)
          this.removeEventListener("message",messageHandler)
          if (data.Ok) resolve(data.Ok);
          else reject(data.Err);
        }
      }
      
      this.waitForConnection().then(() => {
        this.addEventListener("message",messageHandler)
        
        origin = origin || this.endpoint.origin
        dataset = dataset || this.endpoint.dataset
        
        this.send_json({
        // API: sweetheart.asgi3.RestApiEndpoints
          uuid: request_uuid,
          action: "ws.rest.get",
          dataset: dataset, //e.g. table name
          origin: origin //e.g. database name
        })
      })
      .catch((err) => { 
        clearTimeout(timeoutId)
        reject(err) 
      })
    })
  }

  editValue(elt: HTMLTableCellElement, className?: string) {
    if (elt.querySelector("input")) {
      // <input /> element already exists, do nothing.
      return }
    else {

      // Reset dataset when given.
      const eltDataset = elt.dataset.set || this.endpoint.dataset

      // Create an <input /> element, for editing.
      const input = document.createElement("input")
      
      input.value = elt.innerText
      input.type = elt.dataset.input!
      input.className = className || ""
      
      input.oninput = () => {
        // update or insert data in real-time
        if (input.dataset.rowid == "NEW_DATA") {

          this.send_json({
            // API: sweetheart.asgi3.RestApiEndpoints
            action: "ws.rest.post",// insert
            dataset: eltDataset,
            payload: {[elt.dataset.fieldname!]: input.value} 
          }) 
        } else {

          this.send_json({
            // API: sweetheart.asgi3.RestApiEndpoints
            action: "ws.rest.patch",// update
            dataset: eltDataset,
            id: elt.dataset.rowid,
            payload: {[elt.dataset.fieldname!]: input.value}
          }) 
        }
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
