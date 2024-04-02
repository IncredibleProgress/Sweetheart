
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

        allowed = True
        os.sudo(["cp",tempname,f"/etc/systemd/system/{service}.service"],allowed)
        os.sudo(["systemctl","enable",service],allowed)

        os.remove(tempname)


class xDatahub:
    #FIXME

    # schemes = ("http","ws")
    data = {"status":"test-init"}
        
    async def endpoint(self,scope,receive,send):

        if not hasattr(self,"etag"):
            self.etag = hash(datetime.now())

        # ensure here consistency with NginxUnit
        assert scope["http_version"] == "1.1"
        assert scope["asgi"]["version"] == "3.0"
        assert scope["asgi"]["spec_version"] == "2.1"

        headers = dict([ (key.decode("latin-1"),val.decode("latin-1")) 
            for key,val in scope["headers"] ])
        
        if scope["type"] == "http":

            request = await receive()
            # body = request.get("body",b"").decode()

            if headers["x-sweetheart-action"] == "fetch.init":

                assert scope["method"] == "HEAD"
                assert request["type"] == "http.request"

                response = JSONResponse(
                    content = self.data,
                    headers = { "etag": self.etag })
                
        await response(scope,receive,send)
            