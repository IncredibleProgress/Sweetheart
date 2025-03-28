"""
ASGI/3.0 implementation for Sweetheart
which provides Http and Websocket interfaces
"""

import json
from typing import Self
from sweetheart.subprocess import os
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
    """ For raising AsgiEndpoint runtime errors. """
    pass


class HttpResponse(AsgiEndpoint):

    """ Base class and interface for setting Asgi/3 http responses.
        It supports CORS headers and handling of preflight requests. """

    def __init__(self, 
            status: int = 200,# ok status
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

        # response settings
        self.status = status
        self.encoded_headers = headers
        self.encoded_content = content
        
        # default CORS attributes
        self.allow_origin: str = "*" # unsafe
        self.allow_methods: str = "GET"

    def _apply_CORS_policy_(self,
            origin_b: bytes,
            method_b: bytes,
            headers_b: bytes ) -> None:

        self.encoded_CORS_headers = []
        origin = origin.decode("ascii")
        method = method.decode("ascii")
        headers = method.decode("latin-1")

        #1. Handle origin policy
        if "*" in self.allow_origin or origin in self.allow_origin:
            allow_origin = (b"access-control-allow-origin",origin_b)
            self.encoded_CORS_headers.append(allow_origin)
            self.encoded_headers.append(allow_origin)

        #2. Handle methods policy
        if method in self.allow_methods:
            bmethods = self.allow_methods.encode("ascii")
            self.encoded_CORS_headers.append(
                (b"access-control-allow-methods",bmethods))

        #3. Handle headers policy
        if headers and hasattr(self,"allow_headers") \
        and all([h.strip() in self.allow_headers for h in headers.split(",")]):
            bheaders = self.allow_headers.encode("latin-1")
            self.encoded_CORS_headers.append(
                (b"access-control-allow-headers",bheaders))

        #4. Handle max-age policy
        if hasattr(self,"max_age"):
            assert type(self.max_age) is int
            bmax_age = str(self.max_age).encode("latin-1")
            self.encoded_CORS_headers.append(
                (b"access-control-max-age",bmax_age))

        #FIXME: to test and complete
    
    # def getHeaderValue(self,header:str): -> str | None:
    #     """ Get header value from encoded headers with ease. """
        
    #     target = header.lower().encode("latin-1")
    #     headers = dict(self.encoded_headers)
    #     value = headers.get(target)

    #     if not value and hasattr(self,"encoded_CORS_headers"):
    #         # get header within CORS headers
    #         headers = dict(self.encoded_CORS_headers)
    #         value = headers.get(target) 
        
    #     if value is not None:
    #         return value.decode("latin-1")
    
    async def __call__(self,scope,receive,send):

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "http"

        except: raise AsgiRuntimeError(
            "Invalid HttpResponse scope.")

        #! ASGI lowercases http headers
        #! ASGI uppercases http methods
        request_headers = dict(scope["headers"]) # bytes
        gethd = lambda hd: request_headers.get(hd,b"")

        if scope["method"] == "OPTIONS":
            # --- CORS Preflight Requests --- #

            self._apply_CORS_policy_(
                origin_b = gethd(b"origin"),
                method_b = gethd(b"access-control-request-method"),
                headers_b = gethd(b"access-control-request-headers") )

            await send({
                "type": "http.response.start",
                "status": 204, # No Content
                "headers": self.encoded_CORS_headers })

            await send({
                "type": "http.response.body",
                "body": b"" })

        elif scope["method"] in self.allow_methods:
            # --- Mainstream Http Requests --- #

            await send({
                "type": "http.response.start",
                "status": self.status,
                "headers": self.encoded_headers })
            
            await send({
                "type": "http.response.body",
                "body": self.encoded_content })
            
        else: raise AsgiRuntimeError(
            f"Method {scope['method']} not allowed.")


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
        
        # init HttpResponse instance
        super().__init__(content=bjson,**kwargs)

        # set CORS attributes
        self.allow_headers = "content-type, sweetheart-action"

        
class JSONMessage:

    """ Interface for setting Asgi/3 JSON websocket messages.
        Content is encoded as bytes when given type is 'bytes'. """

    def __init__(self,
            content: dict | list[dict],# json
            type: str = "text" ):

        if type == "text":
            self.bytes = None
            self.text = json.dumps(content)

        elif type == "bytes":
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
    def safer(promise:tuple, uuid:str=None) -> Self:
        """ Create encoded JSONMessage from promise. """

        try:
            content = promise[1]
            status = promise[0].capitalize()
            assert status in ("Ok","Err")

        except KeyError:
            raise AsgiRuntimeError(
                "Promise must be tuple of (status,content).")

        except AssertionError:
            raise AsgiRuntimeError(
                "Promise status must be 'Ok' or 'Err'.")
        
        return JSONMessage({ "uuid":uuid, status:content })
        

class Websocket(AsgiEndpoint):

    def on_receive(self,message:dict) -> JSONMessage | None:

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

        # self.scope = scope
        # self.send = send

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "websocket"
            assert list(scope["subprotocols"]) == ["json"]

            # Wait for the WebSocket connect message
            message = await receive()
            assert message["type"] == "websocket.connect"
        
        except:
            raise AsgiRuntimeError(
                "Websocket connection failed.")
        
        # Send WebSocket accept message
        await send({
            "type": "websocket.accept",
            "subprotocol": "json" })

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
                    "Function on_receive() must return JSONMessage instance or None.")
                
            elif message["type"] == "websocket.disconnect":
                # close WebSocket when required
                await send({"type": "websocket.close"})
                break
        
    # async def __del__(self):
    #     await self.send({
    #         "type": "websocket.close", "code": 1011,
    #         "reason": "WebSocket instance deleted at server side." })


class Route:
    """ Interface for setting url path endpoints. """
    # intends to ensure some consistency with starlette.py

    def __init__(self,
        urlpath: str,
        endpoint: AsgiEndpoint,
        methods: str | list[str] = "GET" ):

        self.path = urlpath
        self.endpoint = endpoint

        # set CORS headers for the endpoint:

        if isinstance(methods,str):
            #NOTE: , separated methods exoected
            endpoint.allow_methods = methods.upper()

        elif isinstance(methods,list):
            endpoint.allow_methods = ", ".join(
                [m.upper() for m in methods] )

        else: raise ValueError(
            "Route methods must be str or list of str.")

        
class AsgiLifespanRouter:
    """ Implement ASGI lifespan providing a simple router. """

    def __init__(self,
        # intends to ensure some consistency with Starlette
            routes: list = [],
            debug: bool = BaseConfig.debug,
            middelware: list[tuple] | None = [] ):
        
        self.routes = routes
        self.middelware = middelware or []
        self.middelware.append(("debug",debug))

    async def __call__(self,scope,receive,send):
        #FIXME: should use asynccontextmanager

        if scope["type"] == "lifespan":

            while True:
                message = await receive()

                if message["type"] == "lifespan.startup":

                    middelware = dict(self.middelware)
                    startup = middelware.pop("lifespan.startup",None)
                    shutdown = middelware.pop("lifespan.shutdown",None)

                    scope["status"] = middelware # remaining entries

                    try:
                        #NOTE: startup() must return tuple of (scope,receive,send)
                        if startup: scope,receive,send = startup(scope,receive,send)
                        await send({ "type": "lifespan.startup.complete" })

                    except:
                        await send({
                            "type": "lifespan.startup.failed",
                            "message": "ASGI lifespan startup failed." })
                        
                elif message["type"] == "lifespan.shutdown":
                    
                    if shutdown: shutdown(status=scope["status"])
                    await send({ "type": "lifespan.shutdown.complete" })
                    break

        elif scope["type"] in ("http","websocket"):

            # try matching route from the given url path
            # this implements here a predictable basic router concept
            # which provides the first match found for the given path

            try: 
                route = list( filter(
                    lambda route: route.path == scope["path"], self.routes))[0]
            
            except IndexError: raise AsgiRuntimeError(
                f"No route found for {scope["path"]} in AsgiLifespanRouter.")

            await route.endpoint(scope,receive,send)


class DataHub(Route,AsgiEndpoint):

    def __init__(self,urlpath,datasystem):
        """ Ensure data exchanges with given datasystem. """

        # set Route-like signature
        super().__init__(
            urlpath,
            endpoint = self,# AsgiEndpoint
            methods = "GET, POST, PATCH, PUT, DELETE" )

        # set related data system
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
                "ws.rest.GET": self.ws_REST, "ws.rest.get": self.ws_REST,
                "ws.rest.POST": self.ws_REST, "ws.rest.post": self.ws_REST,
                "ws.rest.PATCH": self.ws_REST, "ws.rest.patch": self.ws_REST }}
    
    # --- --- Dedicated Asgi/3 endpoint --- --- #

    async def __call__(self,scope,receive,send):
        """ Handle HTTP and WebSocket connections. """

        if scope["type"] == "websocket":
            # redirect to Websocket instance
            # which calls on_receive() given hereafter
            await self.websocket(scope,receive,send)
        
        elif scope["type"] == "http":
            #! ASGI lowercases http headers
            #! ASGI uppercases http methods

            request = await receive()
            assert request["type"] == "http.request"

            action = dict(scope["headers"])\
                .get(b"sweetheart-action",b"")\
                .decode('latin-1')

            if action:

                json_response =\
                    self.endpoints["http"][action](scope,request)

                if json_response is not None:
                    await json_response(scope,receive,send)

    # --- --- Websocket processing --- --- #

    def on_receive(self,message:dict) -> JSONMessage | None:
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
            return self.endpoints["websocket"][data["action"]](data) #!

        else: return JSONMessage({"Err":"Invalid websocket action."})

    def ws_ReQL(self,data:dict) -> JSONMessage:
        """ Execute any RethinkDB query from WebSocket. """

        #FIXME: available for development only
        assert os.getenv("SWS_OPERATING_STATE") == "development"

        message: tuple = self.datasystem.rql_expr(data["query"])
        return JSONMessage.safer(message,uuid=data.get("uuid"))

    def ws_REST(self,data:dict) -> JSONMessage:
        """ Hook which handle RESTful API from WebSocket. """ 

        method = data["action"][8:].upper() # ws.rest.get -> GET
        message: tuple = self.datasystem.restapi[method](data)
        if message == ("Ok",None): return None # no message to send back
        return JSONMessage.safer(message,uuid=data.get("uuid"))

    # --- --- Http processing --- --- #

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
                status,value = self.datasystem.restapi["GET"](data)
                return JSONResponse({ status: value })

            case "PATCH":
                data: dict = json.loads(request["body"])
                status,value = self.datasystem.restapi["PATCH"](data)
                assert (status,value) == ("Ok",None) #FIXME
                return JSONResponse({ status: value })

            case "PUT":
                raise NotImplementedError

            case "POST":
                data: dict = json.loads(request["body"])
                status,value = self.datasystem.restapi["POST"](data)
                assert (status,value) == ("Ok",None) #FIXME
                return JSONResponse({ status: value })

            case "DELETE":
                raise NotImplementedError
