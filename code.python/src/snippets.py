
from sweetheart import *

import configparser,hashlib
from datetime import datetime
from urllib.parse import urlparse

from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route,Mount,WebSocketRoute
from starlette.responses import JSONResponse


class xUrl:

    def urlparse(self,url:str):

        parsed_url = urlparse(url)
        # set initial values, it can be changed
        self.protocol = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port


class xWebsocket:

    def set_websocket(self,set_encoding='json'):

        class _WebSocket(WebSocketEndpoint):

            encoding = set_encoding
            receiver = self.on_receive

            async def on_receive(_ws,websocket,data):
                await _ws.receiver(websocket,data)

        self.Websocket = _WebSocket
    
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
            #NOTE: space_around_delimiters must be set at False
            self.sysdconf.write(tempfile, space_around_delimiters=False )
            tempname = tempfile.name

        os.run(["sudo","cp",tempname,f"/etc/systemd/system/{service}.service"])
        os.run(["sudo","systemctl","enable",service])

        os.remove(tempname)


# class xDataHub(UserDict):

#     def push_json(self,data:dict):
#         #FIXME

#         assert data.keys() == ["push"]

#         data.update({
#             "salt": "tMByGcTNg0dhSio0nb",
#             "token": hash(datetime.now()) })
        
#         json_ = json.dumps(data)
#         digest = hashlib.sha1(json_).hexdigest()
#         del data["salt"]

#         return JSONResponse({ 
#             "digest": digest,
#             "data": data })
    
#     def fetch_json(self):
#         raise NotImplementedError
    