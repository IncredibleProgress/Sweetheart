"""
ASGI 3.0 implementation for Sweetheart
which ensures some consistency with starlette
"""

from sweetheart import *


class HttpResponse:

    def __init__(self, 
        status: int = 200,
        content: bytes = b"",
        headers: list[tuple[bytes,bytes]] = [] )-> None:

        self.status = status
        self.headers = headers
        self.content = content

    async def __call__(self,scope,receive,send)-> None:

        assert scope["type"] == "http"

        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self.headers })
        
        await send({
            "type": "http.response.body",
            "body": self.content })


class Route:

    def __init__(self,
        path: str,
        endpoint: HttpResponse,
        methods: list = [] )-> None:

        self.path = path
        self.methods = methods
        self.endpoint = endpoint


class AsgiServerInterface:

    def __init__(self,routes:list=[]):
        
        self.routes = routes
    
    async def __call__(self,scope,receive,send)-> None:

        is_path = lambda route: route.path == scope["path"]

        try:
            route = filter(is_path,self.routes)[0] #!
            assert scope["method"] in route.methods
            endpoint = route.endpoint

        except:
            endpoint = HttpResponse(
                status = 404,
                content = b"404 Not Found",
                headers= [(b"content-type",b"text/plain")] )

        await endpoint(scope,receive,send)


class Websocket:

    def __init__(self,receiver:callable=None):
        
        self.receiver = receiver

    async def __call__(self,scope,receive,send)-> None:

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

    async def send_json(self,data:dict)-> None:

        await self.send({
            "type": "websocket.send",
            "bytes": json.dumps(data).encode() })
        
    # async def __del__(self):
    #     await self.send({"type": "websocket.close"})
        