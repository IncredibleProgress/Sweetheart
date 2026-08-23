"""
ASGI/3.0 implementation for Sweetheart
which provides Http and Websocket interfaces
for handling JSON data exchanges only
"""

import json
from typing import Self, Optional
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
            # ensure scope consistency with ASGI specification
            assert scope["http_version"] == "1.1"
            assert scope["asgi"]["version"] == "3.0"
            assert scope["asgi"]["spec_version"] == "2.1"

class AsgiRuntimeError(Exception):
    """ For raising AsgiEndpoint runtime errors. """
    pass


class HttpResponse(AsgiEndpoint):
    """ Base class and interface for setting Asgi/3 http responses.
        It supports CORS headers and handling of preflight requests. """

    MAX_AGE: Optional[str] = None
    ALLOW_CREDENTIALS: bool = True # safer
    ALLOW_ORIGINS: set[str] = set() # empty - no cross-origin allowance
    ALLOW_HEADERS: set[str] = set() # empty
    EXPOSE_HEADERS: set[str] = set() # empty
    REJECT_METHODS = {"CONNECT","TRACE","TRACK"}

    REJECT_HEADERS = {"accept-charset","accept-encoding","access-control-request-headers",
        "access-control-request-method","connection","content-length","cookie",
        "cookie2","date","dnt","expect","host","keep-alive","origin","referer",
        "te","trailer","transfer-encoding","upgrade","via"}  

    def __init__(self, 
            status: int = 200,# Ok status
            content: bytes | str = b"",
            headers: list[tuple[bytes,bytes]] | dict[str,str] = None):

        if isinstance(content,str):
            # encode content providing charset info
            content = content.encode('utf-8')
            self.content_charset = 'utf-8'#! info only

        if isinstance(headers,dict):
            headers = [
                # latin-1 is default http/1.1 encoding
                (key.encode("latin-1"), val.encode("latin-1"))
                for key,val in headers.items() ]

        # response settings
        self.status: int = status
        self.encoded_headers: list[bytes] = headers or []
        self.encoded_content: bytes = content
        self.allow_methods: set[str] = {"GET"}

    def _apply_CORS_policy_(self,
            origin_b: bytes,
            method_b: bytes,
            headers_b: bytes ) -> (bool,list):

        try:
            origin = origin_b.decode("ascii")
            method = method_b.decode("ascii").upper()
            headers = headers_b.decode("latin-1").strip()#!
        except UnicodeDecodeError:
            return False, []

        #1. Handle origin policy
        if origin not in self.ALLOW_ORIGINS:
            return False, []

        encoded_CORS_headers = [
            (b"access-control-allow-origin", origin_b),
            (b"vary", b"Origin") ]
            
        #2. Handle methods policy
        if not method\
        or method in self.REJECT_METHODS\
        or method not in self.allow_methods:
            return False, []

        encoded_CORS_headers.append((
            b"access-control-allow-methods",
            b", ".join(m.encode("ascii") for m in self.allow_methods)) )

        #3. Handle headers policy
        allow_headers = {h.lower() for h in self.ALLOW_HEADERS}
        reject_headers = {h.lower() for h in self.REJECT_HEADERS}
        received_headers = (
            {h.strip().lower() for h in headers.split(",") if h.strip()}
            if headers else set())

        if received_headers and (
        any(h in reject_headers for h in received_headers)
        or any(h not in allow_headers for h in received_headers)):
            return False, []

        if allow_headers:
            encoded_CORS_headers.append((
                b"access-control-allow-headers",
                b", ".join(h.encode("latin-1") for h in allow_headers)))

        #4. Handle max-age policy
        if self.MAX_AGE and isinstance(self.MAX_AGE,int):
            encoded_CORS_headers.append((
                b"access-control-max-age",
                str(self.MAX_AGE).encode("latin-1")) )

        #5. Handle credentials policy
        if self.ALLOW_CREDENTIALS:
            encoded_CORS_headers.append((
                b"access-control-allow-credentials",
                b"true"))

        # APPROVED -> return CORS headers
        return True, encoded_CORS_headers
    
    async def __call__(self,scope,receive,send):
        """ Endpoint for handling Http responses. """

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "http"
        except:
            raise AsgiRuntimeError("Invalid HttpResponse scope.")

        #! ASGI lowercases http headers, uppercases http methods
        request_headers: dict[bytes,bytes] = dict(scope["headers"])
        def gethdr(hd:bytes)->bytes: return request_headers.get(hd,b"")

        if scope["method"] == "OPTIONS":
            # --- CORS Preflight Requests --- #

            approved,encoded_CORS_headers =(
            # return (False,[]) whith CORS rejected
                self._apply_CORS_policy_(
                    origin_b = gethdr(b"origin"),
                    method_b = gethdr(b"access-control-request-method"),
                    headers_b = gethdr(b"access-control-request-headers")))

            await send({
                "type": "http.response.start",
                "status": 204 if approved else 403 ,# No Content or Forbidden
                "headers": encoded_CORS_headers })

            await send({
                "type": "http.response.body",
                "body": b"" })

        elif scope["method"] in self.allow_methods:
            # --- Mainstream Http Requests --- #
            # add CORS allow-origin header if cross-origin request
            origin: bytes = gethdr(b"origin")
            try:
                if origin and origin.decode("ascii") in self.ALLOW_ORIGINS:
                    self.encoded_headers.extend([
                        (b"access-control-allow-origin", origin),
                        (b"vary", b"Origin") ])
                    if self.ALLOW_CREDENTIALS:
                        self.encoded_headers.append(
                            (b"access-control-allow-credentials", b"true"))
            except UnicodeDecodeError:
                pass #FIXME

            if self.EXPOSE_HEADERS:
                self.encoded_headers.append((
                    b"access-control-expose-headers",
                    b", ".join(h.encode("latin-1") for h in self.EXPOSE_HEADERS) ))

            await send({
                "type": "http.response.start",
                "status": self.status,
                "headers": self.encoded_headers
            })
            await send({
                "type": "http.response.body",
                "body": self.encoded_content })
            
        else:
            # --- Method Not Allowed --- #
            await send({
                "type": "http.response.start",
                "status": 405,# Method Not Allowed
                "headers": [(
                    b"allow", b", ".join(m.encode("ascii") 
                    for m in self.allow_methods) )]
            })
            await send({
                "type": "http.response.body",
                "body": b"" })


class JSONResponse(HttpResponse):
    """Interface for setting Asgi/3 JSON http responses."""
    ALLOW_HEADERS = {"content-type", "sweetheart-action"}

    def __init__(self,
            content: dict | list[dict],
            headers: dict[str,str] = {} ):
        
        bjson = json.dumps(content).encode('utf-8')
        headers.update({
            #NOTE: no bytes here, use str only
            "content-length": str(len(bjson)),
            "content-type": "application/json; charset=utf-8",
            "x-content-type-options": "nosniff" })
        
        # init HttpResponse instance
        super().__init__(
            status= 200, # Ok status
            content= bjson,
            headers= headers )

        
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
    """Interface for setting Asgi/3 WebSocket endpoints."""
    ALLOW_ORIGINS: set[str] = set() # empty - no cross-origin allowance

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

    def _apply_origin_policy_(self,
            headers_lb: list[tuple[bytes,bytes]] ) -> bool:
        """Check if origin is allowed for cross-origin WebSocket connections."""
        try:
            header = dict(headers_lb)[b"origin"]
            origin = header.decode("ascii")
        except (UnicodeDecodeError, KeyError):
            return False
        return origin in self.ALLOW_ORIGINS

    async def __call__(self,scope,receive,send):
        """ Handle WebSocket connections. """

        try:
            super().ensure_versions(scope)
            assert scope["type"] == "websocket"
            assert list(scope["subprotocols"]) == ["json"]#!
            # Wait for the WebSocket connect message
            message = await receive()
            assert message["type"] == "websocket.connect"
        except:
            raise AsgiRuntimeError(
                "Websocket connection failed.")

        header_lb: list[tuple[bytes,bytes]] = scope["headers"]
        accepted_origin = self._apply_origin_policy_(header_lb)
        
        if not accepted_origin:
            # Send WebSocket close message with 403 status code
            await send({
                "type": "websocket.close",
                "code": 403 })
            return
        else:
            # Send WebSocket accept message for json subprotocol
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
        methods: set[str] = {'GET'} ):

        self.path = urlpath
        self.endpoint = endpoint

        #FIXME: set CORS headers for the endpoint:
        assert isinstance(methods,set)
        endpoint.allow_methods = {m.upper() for m in methods}

        
class AsgiLifespanRouter:
    """ Implement ASGI lifespan providing a simple router. """

    def __init__(self,
        # intends to ensure some consistency with Starlette
        routes: list[Route] = [],
        debug: bool = BaseConfig.debug,
        middleware: list[tuple] = [] ):
        
        self.routes = routes
        self.middleware = middleware
        self.middleware.append(("debug",debug))

    async def __call__(self,scope,receive,send):
        #FIXME: should use asynccontextmanager

        if scope["type"] == "lifespan":

            while True:
                message = await receive()

                if message["type"] == "lifespan.startup":

                    #FIXME: to test and complete
                    middleware = dict(self.middleware)
                    startup = middleware.pop("lifespan.startup",None)
                    shutdown = middleware.pop("lifespan.shutdown",None)
                    #NOTE: scope["status"] holds the current app status
                    scope["status"] = middleware # set the remaining entries

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


class RestApiEndpoints(Route,AsgiEndpoint):
    """
    Wrapper which ensures data exchanges with given datasystem
    and through a RESTful API over Http and WebSocket scopes.
    RestApiEndpoints instance is both Route and AsgiEndpoint.
    """

    def __init__(self, urlpath: str, datasystem):

        # set Route-like signature
        Route.__init__(
            self,
            urlpath,
            endpoint = self, # AsgiEndpoint
            methods = {'GET','POST','PATCH','PUT','DELETE'} )

        # set related data system
        self.datasystem = datasystem

        assert hasattr(self.datasystem,"restapi")\
        and isinstance(self.datasystem.restapi,dict),\
            f"Valid REST API not found for {self.datasystem}."

        # set Websocket instance and its receiver
        self.websocket = Websocket()
        self.websocket.on_receive = self.on_receive

        # set Http and Websocket default endpoints
        # only RESTful api is handled here 
        self.endpoints = {
            "http": {
                # "fetch.test": self._fetch_TEST,
                "fetch.rest": self._fetch_REST },
            "websocket": {
                "ws.rest.get": self._ws_REST,
                "ws.rest.post": self._ws_REST,
                "ws.rest.patch": self._ws_REST,
                # "ws.rest.put": self._ws_REST,#FIXME
                # "ws.rest.delete": self._ws_REST,#FIXME
            }}

    # --- --- Dedicated Asgi/3 endpoint --- --- #

    async def __call__(self,scope,receive,send):
        """ Handle HTTP and WebSocket connections.
        Redirect action through sweetheart-action header. """

        if scope["type"] == "websocket":
            # redirect to Websocket instance
            # which calls on_receive() given hereafter
            await self.websocket(scope,receive,send)
        
        elif scope["type"] == "http":
            request = await receive()
            assert request["type"] == "http.request"
            # get sweetheart-action header, lowercased
            #NOTE: ASGI lowercases every http headers
            action = dict(scope["headers"])\
                .get(b"sweetheart-action",b"")\
                .decode('latin-1').lower()
            if action:
                json_response =\
                    self.endpoints["http"][action](scope,request)
                if json_response is not None:
                    await json_response(scope,receive,send)
            else: raise AsgiRuntimeError(
                "Missing 'sweetheart-action' http header.")


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
            action = data["action"].lower()
            return self.endpoints["websocket"][action](data)

        else: return JSONMessage({"Err":"Invalid websocket action."})

    def _ws_REST(self,data:dict) -> JSONMessage:
        """ Hook which handle RESTful API from WebSocket. """

        method = data["action"][8:].upper() # ws.rest.get -> GET
        message: tuple = self.datasystem.restapi[method](data)

        if message == ("Ok",None): return None # no message to send back
        return JSONMessage.safer(message,uuid=data.get("uuid"))
    
    def _ws_edgeQL(self,data:dict) -> JSONMessage:
        """ Execute any Gel/EdgeQL query from WebSocket. """

        #NOTE: available for development only
        assert os.getenv("SWS_OPERATING_STATE") == "development"

        assert hasattr(self.datasystem,"edgeql"),\
            f"Data system {self.datasystem} does not support EdgeQL queries."

        message: tuple = self.datasystem.edgeql(data["query"])
        return JSONMessage.safer(message,uuid=data.get("uuid"))


    # --- --- Http processing --- --- #

    def _fetch_TEST(self,scope,request):
        """ Handle test action from Http. """
        return JSONResponse({ "Test": "Ok" })

    def _fetch_REST(self,scope,request):
        """ Handle RESTful API from Http. """

        match scope["method"]:

            case "GET":
                #NOTE: this assumes query_string is utf-8 encoded
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
