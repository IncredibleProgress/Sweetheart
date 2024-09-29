"""
ASGI 3.0 implementation for Sweetheart
"""

import json
from sweetheart import BaseConfig, ansi, echo, verbose


class AsgiEndpoint:
    """
    Asynchronous Server Gateway Interface\n
    async def __call__(self,scope,receive,send) must be implemented\n
    https://asgi.readthedocs.io/en/latest/
    https://asgi.readthedocs.io/_/downloads/en/latest/pdf/
    """

    @staticmethod
    def ensure_versions(scope):

        verbose("ongoing ASGI scope:",
            f"http version: {scope['http_version']}",
            f"asgi version: {scope['asgi']['version']}",
            f"asgi spec version: {scope['asgi']['spec_version']}",
            level=2 )

        if BaseConfig.debug:
            # ensure scope consistency for using NginxUnit
            assert scope["http_version"] == "1.1"
            assert scope["asgi"]["version"] == "3.0"
            assert scope["asgi"]["spec_version"] == "2.1"


class HttpResponse(AsgiEndpoint):

    def __init__(self, 
            status: int = 200,
            content: bytes | str = b"",
            headers: list[tuple[bytes,bytes]] | dict[str,str] = [] ):

        if isinstance(content,str):
            content = content.encode()

        if isinstance(headers,dict):
            headers = [
                ( key.encode("latin-1"), val.encode("latin-1") )\
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

        bjson = json.dumps(content).encode()
        kwargs["headers"] = kwargs.get("headers",{})

        kwargs["headers"].update({
            #NOTE: no bytes here, str only
            "content-length": str(len(bjson)),
            "content-type": "application/json",
            "x-content-type-options": "nosniff" })
        
        super().__init__(content=bjson,**kwargs)


class Websocket(AsgiEndpoint):

    def receiver(self,message:dict):
        """ must be implemented by Websocket instances """
        raise NotImplementedError

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
                await self.receiver(self,message)
                
            elif message["type"] == "websocket.disconnect":
                # Close WebSocket when required
                await send({"type": "websocket.close"})
                break

    async def send_json(self,data:dict):

        await self.send({
            "type": "websocket.send",
            "bytes": json.dumps(data).encode() })
        
    # async def __del__(self):
    #     await self.send({"type": "websocket.close"})


class Route:
    # set an endpoint for a related url path
    # ensures some consistency with starlette.py

    def __init__(self,
        urlpath: str,
        endpoint: AsgiEndpoint,
        methods: list = ['get','head'] ):

        self.path = urlpath
        self.endpoint = endpoint
        self.methods = [ m.lower() for m in methods]

class AsgiLifespanRouter:
    """
    implement ASGI lifespan and simple router concepts
    """

    def __init__(self,
            routes: list = [],
            debug: bool = True,
            middelware: list = [] ):
        
        self.debug = debug #FIXME
        self.routes = routes

    async def __call__(self,scope,receive,send):

        if scope["type"] == "lifespan":

            while True:
                message = await receive()

                if message["type"] == "lifespan.startup":

                    try:
                        # assert scope["state"]
                        # Do some startup here
                        await send({ "type": "lifespan.startup.complete" })

                    except Exception:
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
                route = filter(
                    lambda route: route.path == scope["path"],
                    self.routes)[0] #! returns first match

                # ensure expected http method is given
                if scope.has_key("method"):
                    assert scope["method"] in route.methods

                # set endpoint from selected route
                endpoint = route.endpoint

            except IndexError:
                # raise an http error response
                endpoint = HttpResponse(
                    status = 404,
                    content = b"404 Not Found",
                    headers= [(b"content-type",b"text/plain")] )

            await endpoint(scope,receive,send)

        else:
            echo("Unknown scope type",scope["type"],prefix=ansi.RED)
            raise NotImplementedError
