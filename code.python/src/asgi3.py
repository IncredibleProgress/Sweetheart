"""
ASGI/3.0 implementation for Sweetheart
"""

import json
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

            # give info at stdout
            verbose("ongoing ASGI scope:",
                f"http version: {scope['http_version']}",
                f"asgi version: {scope['asgi']['version']}",
                f"asgi spec version: {scope['asgi']['spec_version']}")

            # ensure scope consistency with NginxUnit
            assert scope["http_version"] == "1.1"
            assert scope["asgi"]["version"] == "3.0"
            assert scope["asgi"]["spec_version"] == "2.1"


class HttpResponse(AsgiEndpoint):

    def __init__(self, 
            status: int = 200,
            content: bytes | str = b"",
            headers: list[tuple[bytes,bytes]] | dict[str,str] = [] ):

        if isinstance(content,str):
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

        super().ensure_versions(scope)
        assert scope["type"] == "http"

        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self.headers })
        
        await send({
            "type": "http.response.body",
            "body": self.content })


class JSONResponse(HttpResponse):
    # ensures some consistency with starlette.py

    def __init__(self,content:dict,**kwargs):

        bjson = json.dumps(content).encode('utf-8')
        kwargs["headers"] = kwargs.get("headers",{})

        kwargs["headers"].update({
            #NOTE: no bytes here, str only
            "content-length": str(len(bjson)),
            "content-type": "application/json; charset=utf-8",
            "x-content-type-options": "nosniff" })
        
        super().__init__(content=bjson,**kwargs)


class Websocket(AsgiEndpoint):

    def on_message(self,message:dict):
        """ must be implemented by Websocket instance """
        raise NotImplementedError

    async def send_json(self,data:dict):
        await self.send({
            "type": "websocket.send",
            "bytes": json.dumps(data).encode() })

    async def __call__(self,scope,receive,send):

        super().ensure_versions(scope)
        assert scope["type"] == "websocket"

        self.scope = scope
        self.send = send

        # Wait for the WebSocket connect message
        message = await receive()
        assert message["type"] == "websocket.connect"
        
        # Send WebSocket accept message
        await send({
            "type": "websocket.accept",
            "headers": [] }) #FIXME

        while True:
            message = await receive()

            if message["type"] == "websocket.receive":
                # React to incomming WebSocket messages
                await self.on_message(self,message)
                
            elif message["type"] == "websocket.disconnect":
                # Close WebSocket when required
                await send({"type": "websocket.close"})
                break
        
    # async def __del__(self): #FIXME
    #     await self.send({"type": "websocket.close"})


class Route:
    # set an endpoint for a related url path
    # ensures some consistency with starlette.py

    def __init__(self,
        urlpath: str,
        endpoint: AsgiEndpoint,
        methods: list = ['GET'] ):

        self.path = urlpath
        self.endpoint = endpoint
        self.methods = [ m.upper() for m in methods ]


class AsgiLifespanRouter:
    """
    implement ASGI lifespan providing a simple router
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
            
            try:
                # try matching route from the given url path
                # this implements here a basic router concept

                route = list( filter(
                    lambda route: route.path == scope["path"],
                    self.routes ))[0]#! first match

                if "method" in scope:
                    # ensure expected http method is allowed
                    assert scope["method"] in route.methods

                endpoint = route.endpoint

            except:
                endpoint = JSONResponse(
                    status = 500,
                    content = {"Err":"asgi router error occured"})
            
            await endpoint(scope,receive,send)


class DataHub:

    def __init__(self,urlpath,datasystem):
        """ convenient data service endpoint """

        # set Route signature
        self.path = urlpath
        self.endpoint = self
        self.methods = ['GET','POST']

        # set data service
        self.datasystem = datasystem

    async def __call__(self,scope,receive,send):
        
        if scope["type"] == "http":

            try:
                request = await receive()
                assert request["type"] == "http.request"

                for key,val in scope["headers"]:

                    #NOTE: latin-1 is default http/1.1 encoding
                    json_response = self.match_response(
                        header = key.decode('latin-1'),
                        value = val.decode('latin-1'),
                        scope = scope, request = request)

                    if json_response: break

            except:
                json_response = JSONResponse(
                    status = 500,
                    content = {"Err":"asgi datahub error occured"})

            await json_response(scope,receive,send)

        elif scope["type"] == "websocket":

            await self.datasystem.websocket(scope,receive,send)

    def match_response(self,
            header: str, value: str,
            scope: dict, request: dict) -> JSONResponse | None :

        #NOTE:
        # - asgi/unit lowercases http headers
        # - asgi/unit uppercases http methods

        match (header,value,scope["method"]):

            case ("sweetheart-action","fetch.test","GET"):
                return JSONResponse({"test":"ok"})

            # case ("sweetheart-action","fetch.init","GET"):
            #     raise NotImplementedError

            # RESTful API

            case ("sweetheart-action","fetch.rest","GET"):
                body: str = request["body"].decode()
                data: dict = json.loads(body)
                return self.datasystem.restapi["GET"](data)

            # case ("sweetheart-action","fetch.rest","PATCH"):
            #     raise NotImplementedError

            case ("sweetheart-action","fetch.rest","PUT"):
                raise NotImplementedError

            case ("sweetheart-action","fetch.rest","POST"):
                data: dict = json.loads(body)
                return self.datasystem.restapi["POST"](data)

            case ("sweetheart-action","fetch.rest","DELETE"):
                raise NotImplementedError
