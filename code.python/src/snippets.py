
from sweetheart import *

import configparser,hashlib
from urllib.parse import urlparse

from starlette.applications import Starlette
# from starlette.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route,Mount,WebSocketRoute
from starlette.responses import HTMLResponse,FileResponse,JSONResponse,RedirectResponse


class xUrl:

    def urlparse(self,url:str):

        parsed_url = urlparse(url)
        # set initial values, it can be changed
        self.protocol = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port


class xWebsocket:

    def set_websocket(self,dbname=None,set_encoding='json'):

        class _WebSocket(WebSocketEndpoint):

            encoding = set_encoding
            route = f"/data/{dbname}"
            receiver = self.on_receive

            async def on_receive(self,websocket,data):
                await self.receiver(websocket,data)

        self.WebSocketEndpoint = _WebSocket
        verbose("new websocket endpoint: ",_WebSocket.route)
        return _WebSocket.route, _WebSocket
    
    def on_receive(self,websocket,data):
        raise NotImplementedError


class xSystemd:

    # default_systemd_setup = {
    #     'Unit': {
    #         'Description': '[SWEETHEART] Service',
    #         'After': 'network.target' },
    #     'Service': {
    #         'User': os.getuser(),
    #         'ExecStart': f'sh -c "{self.command}"' },
    #     'Install': {
    #         'WantedBy': 'default.target' }}

    def set_systemd_service(self,config:dict)\
        -> configparser.ConfigParser :

        """ create and set config for new systemd service 
            kwargs keys must be supported service options """

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
            #! space_around_delimiters must be set at False
            self.sysdconf.write(tempfile, space_around_delimiters=False )
            tempname = tempfile.name

        os.run(["sudo","cp",tempname,f"/etc/systemd/system/{service}.service"])
        os.run(["sudo","systemctl","enable",service])

        os.remove(tempname)


class xDataHub(UserDict):

    api = { #FIXME
        "auth": {
            "token": str,
            "hash": str,
        },
        "data": {
            "request": {
                "get": str,
                "post": str,
                "put":str,
                "delete": str,
                "ReQL": str,
            },
            "push": {
                "console": str,
                "element": str,
                "attribute": str,
                "value": str,
                "type": str,
            },
            "status": {
                "success": str,
                "error": str,
            }
        },
    }

    def to_push(self,data:dict):

        try:
            api = self.api["data"]["push"].keys()
            assert all([key in api for key in data.keys()])
        except:
            raise Exception("Invalid data given to push")

        data = { "push": "data" }
        digest = hashlib.sha1(data).hexdigest()

        self.data = { 
            "auth": { "hash": digest },
            "data": data }
