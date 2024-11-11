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
        """ must be implemented by AsgiEndpoint instance """
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
    # ensures some consistency with starlette.py

    def __init__(self,
            content: dict | list[dict],
            **kwargs ):

        bjson = json.dumps(content).encode('utf-8')
        kwargs["headers"] = kwargs.get("headers",{})

        kwargs["headers"].update({
            #NOTE: no bytes here, str only
            "content-length": str(len(bjson)),
            "content-type": "application/json; charset=utf-8",
            "x-content-type-options": "nosniff" })
        
        super().__init__(content=bjson,**kwargs)


class JSONMessage():

    def __init__(self,
            content: dict | list[dict],
            type: str = "text" ):

        if self.type == "text":
            self.bytes = None
            self.text = json.dumps(content)

        elif self.type == "bytes":
            self.text = None
            self.bytes = json.dumps(content).encode()

        else: raise ValueError(
            "JSONMessage type must be 'text' or 'bytes'" )
        

class Websocket(AsgiEndpoint):

    def on_receive(self,message:dict):
        """ must be implemented by instance """
        raise NotImplementedError

    async def send_json(self,data:dict):

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data) })

    async def send_bjson(self,data:dict):

        await self.send({
            "type": "websocket.send",
            "bytes": json.dumps(data).encode() })

    async def __call__(self,scope,receive,send):

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
                # react to incomming WebSocket messages
                status = self.on_receive(message)

                if isinstance(status,JSONMessage):
                    # accept JSONMessage as a valid status
                    await send({
                        "type": "websocket.send",
                        "text": status.text,
                        "bytes": status.bytes })
                        
                # ignore any other status
                else: pass
                
            elif message["type"] == "websocket.disconnect":
                # Close WebSocket when required
                await send({"type": "websocket.close"})
                break
        
    async def __del__(self):
        await self.send({"type": "websocket.close"})


class Route:
    # set an endpoint for a related url path
    # ensures some consistency with starlette.py

    def __init__(self,
        urlpath: str,
        endpoint: AsgiEndpoint,
        methods: list = ['GET'] ):

        self.path = urlpath
        self.endpoint = endpoint
        self.methods = [m.upper() for m in methods]


class AsgiLifespanRouter:
    """
    Implement ASGI lifespan providing a simple router.
    """

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
                        # Do some startup here
                        await send({ "type": "lifespan.startup.complete" })

                    except:
                        await send({
                            "type": "lifespan.startup.failed",
                            "message": "missing state starting lifespan" })
                        
                elif message["type"] == "lifespan.shutdown":

                    # Do some shutdown here
                    await send({ "type": "lifespan.shutdown.complete" })
                    break

        elif scope["type"] in ("http","websocket"):
            
            # try matching route from the given url path
            # this implements here a basic router concept
            route = list( filter(
                lambda route: route.path == scope["path"],
                self.routes ))[0]#! first match

            if "method" in scope:
                # ensure expected http method is allowed
                assert scope["method"] in route.methods
            
            await route.endpoint(scope,receive,send)


class DataHub:

    def __init__(self, urlpath, datasystem):
        """ convenient data service endpoint """

        # set Route signature
        self.path = urlpath
        self.endpoint = self
        self.methods = ['GET','POST','PATCH','PUT','DELETE']

        # set data service
        datasystem.connect()
        self.datasystem = datasystem

    async def __call__(self,scope,receive,send):

        if scope["type"] == "websocket":

            await self.datasystem.websocket(scope,receive,send)
        
        elif scope["type"] == "http":

            request = await receive()
            assert request["type"] == "http.request"

            for key,val in scope["headers"]:

                #NOTE: latin-1 is default http/1.1 encoding
                json_response = self._match_case_(
                    header = key.decode('latin-1'),
                    value = val.decode('latin-1'),
                    scope = scope, request = request)

                if json_response: break

            await json_response(scope,receive,send)

    def _match_case_(self,
            header: str,
            value: str,
            scope: dict,
            request: dict) -> JSONResponse | None :

        match (header,value,scope["method"]):

            #NOTE:
            # - asgi/unit lowercases http headers
            # - asgi/unit uppercases http methods

            case ("sweetheart-action","fetch.test","GET"):
                return JSONResponse({"test":"ok"})

            # RESTful API implementation:

            case ("sweetheart-action","fetch.rest","GET"):
                #! assumes query_string is utf-8 encoded
                query: str = "?"+scope["query_string"].decode()
                data: dict = urlparse_qs(query,strict_parsing=True)
                return self.datasystem.restapi["GET"](data)

            case ("sweetheart-action","fetch.rest","PATCH"):
                raise NotImplementedError

            case ("sweetheart-action","fetch.rest","PUT"):
                raise NotImplementedError

            case ("sweetheart-action","fetch.rest","POST"):
                raise NotImplementedError

            case ("sweetheart-action","fetch.rest","DELETE"):
                raise NotImplementedError
