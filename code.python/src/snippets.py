
from sweetheart import *
from sweetheart.asgi3 import *

import configparser,hashlib
from datetime import datetime
from urllib.parse import urlparse

# [Deprecated]
# from starlette.applications import Starlette
# from starlette.endpoints import WebSocketEndpoint
# from starlette.routing import Route,Mount,WebSocketRoute
# from starlette.responses import JSONResponse


class xUrl:

    def urlparse(self,url:str):

        parsed_url = urlparse(url)

        # set url attributes
        self.protocol = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port


class xSystemd:

    def set_systemd_service(self,config:dict)\
        -> configparser.ConfigParser :

        """ create and set config for new systemd service 
            config keys must be supported service options """

        # provide a ConfigParser for setting systemd
        self.sysdconf = configparser.ConfigParser()
        self.sysdconf.optionxform = str #! keep case of options 

        # set sections of systemd service file
        self.sysdconf.add_section('Unit')
        self.sysdconf.add_section('Service')
        self.sysdconf.add_section('Install')

        for section in config.keys():
            assert section in ('Unit','Service','Install')
            for option,value in config[section].items():
                if BaseConfig.debug and option not in {

                    '[Unit]':
                        ('Description','After','Before'),
                    '[Service]':
                        ('ExecStart','ExecReload','Restart','Type','User','Group',
                        'StandardOutput','StandardError','SyslogIdentifier'),
                    '[Install]':
                        ('WantedBy','RequiredBy') }[section]:

                    verbose(f"option '{option}' setting systemd : to check",
                        level=0, prefix=ansi.RED)

                # set option given with config
                self.sysdconf[section][option] = value

    def enable_systemd_service(self,service:str):

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            #NOTE: space_around_delimiters must be set at False
            self.sysdconf.write(tempfile, space_around_delimiters=False )
            tempname = tempfile.name

        os.run(["sudo","cp",tempname,f"/etc/systemd/system/{service}.service"])
        os.run(["sudo","systemctl","enable",service])

        os.remove(tempname)


class xDataHub:
    #FIXME

    def _App_init(self,request):

        if not hasattr(self,"token"):
            self.token = bytes(hash(datetime.now()))

        return JSONResponse(
            content = self.data,
            headers = {
                "X-Sweetheart-Action": "init",
                "X-Sweetheart-Token": self.token })
    
    def _ReQL_update(self,request):
        pass
        
    async def endpoint(self,request):

        method = request.method.uppers()
        action = request.headers["X-Sweetheart-Action"]
        token = request.headers["X-Sweetheart-Token"]

        assert  token == self.token


# class xWebsocket:
        
#     """ former websocket implementation with Starlette """

#     def set_websocket(self,set_encoding='json'):
#         assert set_encoding in ('json','bytes','text')

#         class _WebSocket(WebSocketEndpoint):

#             encoding = set_encoding
#             receiver = self.on_receive

#             # async def on_connect(self,websocket):
#             #   await websocket.accept()

#             async def on_receive(_ws,websocket,data):
#                 await _ws.receiver(websocket,data)

#             # async def on_disconnect(self,websocket,close_code):
#             #     pass

#         self.Websocket = _WebSocket
    
#     def on_receive(self,websocket,data):
#         raise NotImplementedError
