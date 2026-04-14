import json
from typing import Self
from pathlib import Path

from sweetheart import *
from sweetheart.subprocess import os,stat
from sweetheart.systemctl import Caddy,PythonApp

from sweetheart.asgi3 import (
    AsgiLifespanRouter, RestApiEndpoints, Route, 
    Websocket, JSONResponse, JSONMessage )


class PostgresUnchained():
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

    def connect(self,settings={}):
        
        from gel import create_client # [LocalImport]
        assert isinstance(settings,dict)

        #FIXME: set default settings as kwargs
        kwargs = dict()
        kwargs.update(settings)

        os.chdir(self.PATH) #FIXME
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


class TimescaleDB():
    """
    real-time analytics on time-series data with Postgres
    https://docs.tigerdata.com/#TimescaleDB
    """
    # Not Implemented

class DocumentDB():
    """
    MongoDB compatible document database with Postgres
    https://documentdb.io
    """
    # Not Implemented


class DataHub(RestApiEndpoints):

    def __init__(self, urlpath:str, datasystem):

        super().__init__(urlpath,datasystem)
        datasystem.PATH = WebappServer._config_[urlpath] #FIXME

        self.endpoints["websocket"].update({
            # default endpoints
            #NOTE: provided by RestApiEndpoints
            # "ws.rest.get": self._ws_REST,
            # "ws.rest.post": self._ws_REST,
            # "ws.rest.patch": self._ws_REST,
            
            # further DataHub endpoints
            "ws.edgeql": self._ws_EdgeQL,
            # "ws.reql": self._ws_ReQL,
        }) 

    def _ws_EdgeQL(self,data:dict) -> JSONMessage:
        """ Execute any Gel/EdgeQL query from WebSocket. """

        #NOTE: available for development only
        assert os.getenv("SWS_OPERATING_STATE") == "development"

        # ensure datasystem is PostgresUnchained
        assert isinstance(self.datasystem,PostgresUnchained)

        message: tuple = self.datasystem.edgeql(data["query"])
        return JSONMessage.safer(message,uuid=data.get("uuid"))

    # [Deprecated]
    # def _ws_ReQL(self,data:dict) -> JSONMessage:
    #     """ Execute any RethinkDB query from WebSocket. """

    #     #NOTE: available for development only
    #     assert os.getenv("SWS_OPERATING_STATE") == "development"

    #     message: tuple = self.datasystem.rql_expr(data["query"])
    #     return JSONMessage.safer(message,uuid=data.get("uuid"))


class WebappServer(Caddy,PythonApp):

    def __init__(self, config:BaseConfig):
        
        self.data = []
        self.config = config
        self.python_app = "python_app"
        self.shared_content = "shared_content"
        self.middleware = [] #FIXME
        
        WebappServer._config_ = config 

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

    def set_service(self, systemctl:bool=False):

        # Expose webapp statics
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

        # Set python app from config
        pyconf = self.config[self.python_app]
        pyfile = Path(pyconf['path'])/pyconf['module']

        #FIXME: avoid extension matter with module name
        module, extension = pyfile.stem, pyfile.suffix
        if extension==".py": pyconf['module'] = module
        else: pyfile = pyfile.with_suffix('.py')

        pyfile.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
        pyfile.write_text(self.generate_python_script)

        if systemctl is True:
            #FIXME: Set systemctl for Caddy web server and Python app

            settings = self.config[self.python_app]
            settings["venv"] = settings["venv"] or self.config.python_env
            verbose(f"Set Python app service with venv: {settings['venv']}")

            self.set_uvicorn_service(settings)
            self.enable_uvicorn_service(settings["sysd"])

            caddyfile = Path(self.config.caddyfile)
            caddyfile.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
            caddyfile.write_text(self.generate_caddyfile)

            self.set_caddy_service(caddyfile)
            self.enable_caddy_service("caddy.service")

            # [Deprecated] 
            # put NginxUnit config for python app
            # self.load_unit_config(source="conffile")
            # self.set_unit_config(share_directory=True)
            # Unit.put_unit_config()

    @property
    def generate_caddyfile(self) -> str:

        python_app = self.config[self.python_app]
        shared_content = self.config[self.shared_content]

        return f"""# --- start Caddyfile script --- #

#FIXME: https support with TLS certificates
http://localhost:8080 {{
    reverse_proxy unix//{python_app["uds"][1:]}
    root * {shared_content["chroot"]}
    file_server {{
        index {shared_content["index"]}
    }}
}}

# --- end of script --- #"""

    @property
    def generate_python_script(self) -> str:

        python_app = self.config[self.python_app]
        assert not python_app["callable"].endswith(".py")

        return f"""# --- start Python3 script --- #

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

{python_app["callable"]} = WebappServer(config).app(
    # DataHub("/tsdata", TimescaleDB()), # NotImplemented
    DataHub("/geldata", PostgresUnchained()),
)

# --- end of script --- #"""