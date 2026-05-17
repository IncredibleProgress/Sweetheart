from pathlib import Path
from typing import Self,Optional,Callable

from sweetheart import *
from sweetheart.subprocess import os,stat
from sweetheart.systemctl import Caddy,PythonApp

from sweetheart.asgi3 import (
    AsgiLifespanRouter, RestApiEndpoints, Route, 
    Websocket, JSONResponse, JSONMessage )


class DataSystem:
    """ Base class for data systems """


class DataHub(RestApiEndpoints):

    def __init__(self, urlpath:str, datasystem:DataSystem):

        """" DataHub is a Http/WebSocket endpoint for data traffic, which is related 
        to a given data system e.g. PostgresUnchained, TimescaleDB, DocumentDB, etc.
        It provides REST API endpoints, and can be extended with custom endpoints. """

        super().__init__(urlpath,datasystem)
        datasystem.dbpth = WebappServer._settings_("dbpth")
        
        self.endpoints["websocket"].update({
            # REST endpoints (set by RestApiEndpoints)
            # "ws.rest.get": self._ws_REST,
            # "ws.rest.post": self._ws_REST,
            # "ws.rest.patch": self._ws_REST,
            # "ws.rest.put": self._ws_REST,
            # "ws.rest.delete": self._ws_REST,
            
            #NOTE: enable DataHub endpoints
            "ws.edgeql": self._ws_edgeQL,
            # "ws.reql": self._ws_ReQL,
        }) 


class WebappServer(PythonApp):

    def __init__(self, config:BaseConfig):
        
        self.data = []
        self.config = config
        self.settings = "localhost" #default
        self.middleware = [] #FIXME
        
        # provide current settings via class
        WebappServer._settings_: Callable[[str],Optional[str]] =\
            lambda key: self.config[self.settings].get(key)

    def mount(self, *args: Route|DataHub ) -> Self:

        # unrelevant instances forbidden
        allowed = (Route,DataHub)
        assert all([isinstance(arg,allowed) for arg in args])
        
        self.data.extend(args)
        return self

    def app(self, *args: Route|DataHub ) -> AsgiLifespanRouter:

        """ Return ASGI app built from given args, callable by NginxUnit. 
            Intends to keep some consistency with https://www.starlette.io."""

        # mount args with mount() or app() but not both
        if args:
            assert self.data == []
            self.mount(*args)
        
        routes = self.data
        del self.data #! new mount forbidden

        return AsgiLifespanRouter(
            routes = routes,
            debug = BaseConfig.debug,
            middleware = self.middleware )

    def set_service(self, systemctl=False, caddy=False):
        """ Set up services for webapp and Caddy web server. """

        settings = self.config[self.settings]
        assert settings["type"] == self.__class__.__name__

        # add attributes for convenience
        self.python_app_uri = settings["data"].split(":")[0]
        self.python_app = settings["data"].split(":")[1]
        self.shared_content = settings["html"]
        
        #1. Expose webapp statics from config

        exposed_path = self.config[self.shared_content]["chroot"]
        exposed_parts = Path(exposed_path).parts

        assert os.isdir(exposed_path),\
            f"{exposed_path} must be a valid directory path"

        #FIXME: ensure permissions
        for i in range(1,len(exposed_parts)+1):
            curpth = Path(*exposed_parts[:i])
            st_mode = os.stat(curpth).st_mode
            if st_mode & stat.S_IXOTH == 0 :
                verbose(f"add execute permission to {curpth} directory")
                os.chmod(curpth, st_mode|stat.S_IXOTH)

        #2. Set Python app from config

        pyconf = self.config[self.python_app]
        pyconf["venv"] = pyconf["venv"] or self.config.python_env
        verbose(f"Set Python app service with venv: {pyconf['venv']}")

        # set related uvicorn ASGI service 
        self.set_uvicorn_service(pyconf,self.generate_python_script)
        if systemctl: self.enable_uvicorn_service(pyconf["sysd"])

        # set a Caddyfile snippet for webapp
        Caddy.caddylist.append(self.generate_caddyfile)

        if caddy is True:
            Caddy.set_caddy_instance(systemctl)
            Caddy.instance.set_caddy_service(self.config.caddyfile)
            if systemctl: Caddy.instance.enable_caddy_service()

    @property
    def generate_caddyfile(self) -> str:

        pyconf = self.config[self.python_app]
        shared = self.config[self.shared_content]
        assert pyconf["uds"].startswith("/")

        return f"""
{ self.getv("url") } {{
    handle_path { self.python_app_uri }* {{
        reverse_proxy unix/{ pyconf["uds"][1:] }
    }}
    root * { shared["chroot"] }
    file_server {{
        index { shared["index"] }
    }}
}}
"""
    @property
    def generate_python_script(self) -> str:

        pyconf = self.config[self.python_app]
        assert not pyconf["callable"].endswith(".py")

        return f"""
# Import Sweetheart Services:
from sweetheart.services import *

# Set App Configuration:

config = set_config({{
    # set here your own app config when required
    # but please refer to the documentation first
}})

# Set Python Asgi/3 App for data:

# create here a runable entry point for your data traffic
# default and recommended is a PostgresUnchained data driver at the url /geldata
# NOTE: Sweetheart aims to serve statics directly via Caddy, not Asgi/3

{ pyconf["callable"] } = WebappServer(config).app(
    # DataHub("/tsdata", TimescaleDB()), # NotImplemented
    DataHub({ self.python_app_uri }, PostgresUnchained()),
)
"""


  #############################################################################
 ##  Data System Classes  ####################################################
#############################################################################

class PostgresUnchained(DataSystem):
    #FIXME: incomplete, untested

    def __init__(self):

        self.restapi = {
            #NOTE: methods are uppercased
            "GET": self._SELECT_,
            "POST": self._INSERT_,
            "PATCH": self._UPDATE_,
            # "PUT": self.edgeQL_REPLACE,
            # "DELETE": self.edgeQL_DELETE
        }

    def connect(self, settings={}):
        
        from gel import create_client # [LocalImport]
        assert isinstance(settings,dict)

        #FIXME: set default settings as kwargs
        kwargs = dict()
        kwargs.update(settings)

        #FIXME: set path of gel project
        assert self.dbpath is not None
        os.chdir(self.dbpath)
        
        self.client = create_client(**kwargs)
        self.client.ensure_connected()

        return self.client
    
    def edgeql(self,query:str,client=None) -> tuple:
    
        if client is None:
            client = self.client

        # return result as tuple (status, value)
        return "Ok", client.query(query)

    def _SELECT_(self,d:dict,client=None) -> tuple:
        
        if client is None:
            client = self.client

        query = client.query(f"""
            select {d['table']};
        """)

        # return result as tuple (status, value)
        return "Ok", query

    def _INSERT_(self,d:dict,client=None) -> tuple:

        if client is None:
            client = self.client

        #FIXME: convert dict to edgeQL object notation
        data: str = ", ".join([
            f"{k}: {v if isinstance(v,(int,float)) else f'\"{v}\"'}" \
            for k,v in d["row"].items() ]) 

        #FIXME: ensure data is not empty
        assert data != ""

        query = client.query(f"""
            insert {d['table']} {{ {data} }};
        """)

        # return result as tuple (status, value)
        return "Ok", query

    def _UPDATE_(self,d:dict,client=None) -> tuple:

        if client is None:
            client = self.client

        #FIXME: convert value to edgeQL object notation
        if not isinstance(d["value"],(int,float)):
            d["value"] = f'"{d["value"]}"' # add quotes

        query = client.query(f"""
            update {d['table']}
            filter .id = {d['id']}
            set {{ .{d['name']} := {d['value']} }};
        """)

        # return result as tuple (status, value)
        return "Ok", query

    def set_service(self,enable:str=None):
        raise NotImplementedError


class TimescaleDB(DataSystem):
    """
    real-time analytics on time-series data with Postgres
    https://docs.tigerdata.com/#TimescaleDB
    """
    # Not Implemented

class DocumentDB(DataSystem):
    """
    MongoDB compatible document database with Postgres
    https://documentdb.io
    """
    # Not Implemented
