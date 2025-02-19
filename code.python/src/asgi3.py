"""
ASGI/3.0 implementation for Sweetheart
"""

import json
from sweetheart.urllib import urlparse_qs
from sweetheart import BaseConfig, ansi, echo, verbose


class AsgiEndpoint:
    """
    Asynchronous Server Gateway Interface\n
    https://asgi.readthedocs.io/en/latest/
    https://asgi.readthedocs.io/_/downloads/en/latest/pdf/
    """

    async def __call__(self,scope,receive,send):
        """ Must be implemented by AsgiEndpoint instance. """
        raise NotImplementedError

    @staticmethod
    def ensure_versions(scope):

        if BaseConfig.debug:
            # ensure scope consistency with NginxUnit
            assert scope["http_version"] == "1.1"
            assert scope["asgi"]["version"] == "3.0"
            assert scope["asgi"]["spec_version"] == "2.1"

class AsgiRuntimeError(Exception):
    pass


class HttpResponse(AsgiEndpoint):

    def __init__(self, 
            status: int = 200,
            content: bytes | str = b"",
            headers: list[tuple[bytes,bytes]] | dict[str,str] = [] ):

        if isinstance(content,str):
            # encode content providing charset info
            content = content.encode('utf-8')
            self.content_charset = 'utf-8'#! info only

        if isinstance(headers,dict):
            headers = [# latin-1 is default http/1.1 encoding
                ( key.encode("latin-1"), val.encode("latin-1") )
                for key,val in headers.items() ]

        self.status = status
        self.headers = headers
        self.content = content
        
    async def __call__(self,scope,receive,send):

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "http"

        except:
            raise AsgiRuntimeError("HttpResponse failed")

        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self.headers })
        
        await send({
            "type": "http.response.body",
            "body": self.content })

class JSONResponse(HttpResponse):

    """ Interface for setting Asgi/3 JSON http responses. """
    # intends to ensure some consistency with starlette.py

    def __init__(self,
            content: dict | list[dict],
            **kwargs ):

        bjson = json.dumps(content).encode('utf-8')
        kwargs["headers"] = kwargs.get("headers",{})

        kwargs["headers"].update({
            #NOTE: no bytes here, use str only
            "content-length": str(len(bjson)),
            "content-type": "application/json; charset=utf-8",
            "x-content-type-options": "nosniff" })
        
        super().__init__(content=bjson,**kwargs)


class JSONMessage:

    """ Interface for setting Asgi/3 JSON websocket messages.
        Content is encoded as bytes when type is 'bytes'. """

    def __init__(self,
            content: dict | list[dict],# json
            type: "text"|"bytes" = "text" ):

        if self.type == "text":
            self.bytes = None
            self.text = json.dumps(content)

        elif self.type == "bytes":
            self.text = None
            #NOTE: content is here encoded as bytes
            self.bytes = json.dumps(content).encode()

        else: raise ValueError(
            "JSONMessage type must be 'text' or 'bytes'" )

    # def __str__(self):
    #     return self.text or self.bytes.decode()

    # def __bytes__(self):
    #     return self.bytes or self.text.encode()

    @staticmethod
    def encode_from(promise: tuple[str, str|dict|list]) -> JSONMessage:
        """ Create encoded JSONMessage from promise. """

        status, content = promise[0].capitalize(), promise[1]

        assert status in ("Ok","Unsafe","Err")
        return JSONMessage({ status: content }, type="bytes")
        

class Websocket(AsgiEndpoint):

    def on_receive(self,message:dict):
        """ Hook for handling incoming messages, which must be implemented by instance.
        It should return a JSONMessage instance for sending to the client or None. """

        raise NotImplementedError

    async def send_json(self,data:dict):
        """ Send JSON data as text to the client. """

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data) })

    async def send_bjson(self,data:dict):
        """ Send JSON data as bytes to the client. """

        await self.send({
            "type": "websocket.send",
            "bytes": json.dumps(data).encode() })

    async def __call__(self,scope,receive,send):
        """ Handle WebSocket connections. """

        self.scope = scope
        self.send = send

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "websocket"

            # Wait for the WebSocket connect message
            message = await receive()
            assert message["type"] == "websocket.connect"
        
        except:
            raise AsgiRuntimeError("Websocket failed")
        
        # Send WebSocket accept message
        await send({"type": "websocket.accept"})

        while True:
            message = await receive()

            if message["type"] == "websocket.receive":
                # handle incomming WebSocket messages
                # self.on_receive() method must be implemented by instance
                json_message = self.on_receive(message)

                if isinstance(json_message,JSONMessage):
                    await send({
                        "type": "websocket.send",
                        "text": json_message.text,
                        "bytes": json_message.bytes })
                        
                elif json_message is None:
                    # no feedback here to the client, just
                    pass

                else: raise ValueError(
                    "on_receive() must return JSONMessage instance or None")
                
            elif message["type"] == "websocket.disconnect":
                # close WebSocket when required
                await send({"type": "websocket.close"})
                break
        
    async def __del__(self):
        #FIXME: ensure WebSocket is closed
        await self.send({"type": "websocket.close"})


class Route:
    """ Interface for setting url path endpoints. """
    # intends to ensure some consistency with starlette.py

    def __init__(self,
        urlpath: str,
        endpoint: AsgiEndpoint,
        methods: list = ['GET'] ):

        self.path = urlpath
        self.endpoint = endpoint
        self.methods = [m.upper() for m in methods]


class AsgiLifespanRouter:
    """ Implement ASGI lifespan providing a simple router. """

    def __init__(self,
            routes: list = [],
            debug: bool = BaseConfig.debug,
            middelware: list = [] ):
        
        self.debug = debug #FIXME
        self.routes = routes

    async def __call__(self,scope,receive,send):

        if scope["type"] == "lifespan":

            while True:
                message = await receive()

                if message["type"] == "lifespan.startup":

                    try:
                        # assert scope["state"] #FIXME
                        # Do some startup here, provided by middleware
                        await send({ "type": "lifespan.startup.complete" })

                    except:
                        await send({
                            "type": "lifespan.startup.failed",
                            "message": "missing state starting lifespan" })
                        
                elif message["type"] == "lifespan.shutdown":

                    # Do some shutdown here, provided by middleware
                    await send({ "type": "lifespan.shutdown.complete" })
                    break

        elif scope["type"] in ("http","websocket"):

            # try matching route from the given url path
            # this implements here a predictale basic router concept
            # which provides the first match found for the given path

            route = list( filter(
                lambda route: route.path == scope["path"], self.routes))[0]

            if scope.get("method"):
                # ensure expected http method is allowed
                assert scope["method"] in route.methods
            
            await route.endpoint(scope,receive,send)


class DataHub(AsgiEndpoint):

    def __init__(self, urlpath, datasystem):
        """ Ensure data exchanges with given datasystem. """

        # set Route-like signature
        self.path = urlpath
        self.endpoint = self
        self.methods = ['GET','POST','PATCH','PUT','DELETE']

        # init given data service
        datasystem.connect()
        self.datasystem = datasystem
        
        # set Websocket instance and its receiver
        self.websocket = Websocket()
        self.websocket.on_receive = self.on_receive

        # set Http and Websocket methods
        self.endpoints = {

            "http": {
                "fetch.test": self.fetch_TEST,
                "fetch.rest": self.fetch_REST },

            "websocket": {
                "ws.reql": self.ws_ReQL,
                "ws.rest.GET": self.ws_REST,
                "ws.rest.POST": self.ws_REST,
                "ws.rest.PATCH": self.ws_REST }}
    
    # --- --- Dedicated Asgi/3 endpoint --- ---

    async def __call__(self, scope, receive, send):
        """ Handle HTTP and WebSocket connections. """

        if scope["type"] == "websocket":

            # redirect to Websocket instance
            # which calls on_receive() given hereafter

            await self.websocket(scope,receive,send)
        
        elif scope["type"] == "http":

            request = await receive()
            assert request["type"] == "http.request"

            #! asgi/unit lowercases http headers
            #! asgi/unit uppercases http methods

            # process http headers for finding action
            for key,val in scope["headers"]:

                #NOTE: latin-1 is default http/1.1 encoding
                header = key.decode('latin-1')
                method = val.decode('latin-1')

                # Do some header processing here
                if header == "sweetheart-action":
                    
                    json_response = \
                        self.endpoints["http"][method](scope,request)

                    if json_response is not None:
                        await json_response(scope,receive,send)
                        break
    
    # --- --- Websocket processing --- ---

    def on_receive(self, message:dict) -> JSONMessage | None:
        """ Handle incoming Asgi/3 WebSocket messages. """
        
        if message.get("text"):
            # get json content from text
            assert message.get("bytes") is None #FIXME
            data: dict = json.loads(message["text"])

        elif message.get("bytes"):
            # get json content from bytes
            data: dict = json.loads(message["bytes"].decode())

        if data.get("action") in self.endpoints["websocket"]:
            # redirect to dedicated websocket action
            return self.endpoints["websocket"][data["action"]](data)

        else: return JSONMessage.encode_from(
            ("Err", "Invalid websocket action.") )

    def ws_ReQL(self, data:dict) -> JSONMessage:
        """ Execute any RethinkDB query from WebSocket. """

        #FIXME: available only for development mode
        assert os.getenv("SWS_OPERATING_STATE") == "development"

        status, value = self.datasystem.rql_expr(data["query"])
        return JSONMessage.encode_from((status, value))

    def ws_REST(self, data:dict) -> JSONMessage:
        """ Hook which handle RESTful API from WebSocket. """ 

        method = data["action"][8:].upper()# ws.rest.get -> GET 
        promise = self.datasystem.restapi[method](data)
        return JSONMessage.encode_from(promise)

    # --- --- Http processing --- ---

    def fetch_TEST(self,scope,request):
        """ Handle test action from Http. """

        return JSONResponse({ "test": "ok" })

    def fetch_REST(self,scope,request):
        """ Handle RESTful API from Http. """

        match scope["method"]:

            case "GET":
                #! this assumes query_string is utf-8 encoded
                query: str = "?"+scope["query_string"].decode()
                data: dict = urlparse_qs(query,strict_parsing=True)
                status, value = self.datasystem.restapi["GET"](data)
                return JSONResponse({ status: value })

            case "PATCH":
                data: dict = json.loads(request["body"])
                status, value = self.datasystem.restapi["PATCH"](data)
                assert (status,value) == ("Ok",None) #FIXME
                return JSONResponse({ status: value })

            case "PUT":
                raise NotImplementedError

            case "POST":
                data: dict = json.loads(request["body"])
                status, value = self.datasystem.restapi["POST"](data)
                assert (status,value) == ("Ok",None) #FIXME
                return JSONResponse({ status: value })

            case "DELETE":
                raise NotImplementedError
