"""
ASGI 3.0 implementation for Sweetheart
ensures some consistency with starlette
"""

from sweetheart import *


class AsgiEndpoint:
    """
    Asynchronous Server Gateway Interface\n
    async def __call__(self,scope,receive,send) must be implemented\n
    https://asgi.readthedocs.io/en/latest/
    https://asgi.readthedocs.io/_/downloads/en/latest/pdf/
    """


class Route:

    def __init__(self,
        path: str,
        endpoint: AsgiEndpoint,
        methods: list = [] ):

        self.path = path
        self.methods = methods
        self.endpoint = endpoint


class Asgi3App:

    def __init__(self,
        routes: list = [],
        debug: bool = True,
        middelware: list = [] ):
        
        self.routes = routes
    
    async def __call__(self,scope,receive,send):

        is_path = lambda route: route.path == scope["path"]

        try:
            route = filter(is_path,self.routes)[0] #!

            if scope.has_key("method"):
                assert scope["method"] in route.methods

            endpoint = route.endpoint

        except:
            endpoint = HttpResponse(
                status = 404,
                content = b"404 Not Found",
                headers= [(b"content-type",b"text/plain")] )

        await endpoint(scope,receive,send)


class HttpResponse(AsgiEndpoint):

    def __init__(self, 
        status: int = 200,
        content: bytes|str = b"",
        headers: list[tuple[bytes,bytes]]|dict = [] ):

        if isinstance(content,str):
            content = content.encode()

        if isinstance(headers,dict): headers = [
            ( key.encode("latin-1"), val.encode("latin-1") )\
            for key,val in headers.items() ]

        self.status = status
        self.headers = headers
        self.content = content

    async def __call__(self,scope,receive,send):

        assert scope["type"] == "http"

        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self.headers })
        
        await send({
            "type": "http.response.body",
            "body": self.content })
        

class Lifespan(AsgiEndpoint):
    #FIXME
    
    def __init__(self,receiver:callable):
        
        self.receiver = receiver

    async def __call__(self,scope,receive,send):

        assert scope["type"] == "lifespan"

        message = await receive()
        assert message["type"] == "lifespan.startup"

        try:
            assert scope["state"]
            # Do some startup here
            await send({ "type": "lifespan.startup.complete" })

        except:
            await send({
                "type": "lifespan.startup.failed",
                "message": "missing state starting lifespan" })

        while True:
            message = await receive()

            if message["type"] == "lifespan.shutdown":
                # Do some shutdown here
                await send({ "type": "lifespan.shutdown.complete" })
                break

            self.receiver(scope,receive,send)


class Websocket(AsgiEndpoint):

    def __init__(self,receiver:callable):
        
        self.receiver = receiver

    async def __call__(self,scope,receive,send):

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
        