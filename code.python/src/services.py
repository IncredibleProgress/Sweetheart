from sweetheart import *
from typing import Self
from pathlib import Path
# from rethinkdb import RethinkDB as R
from sweetheart.systemctl import Unit, Systemd

from sweetheart.asgi3 import (
    AsgiLifespanRouter, RestApiEndpoints, Route, 
    Websocket, JSONResponse, JSONMessage )


class PostgresUnchained():
    #FIXME: incomplete, untested

    def __init__(self, config:BaseConfig=None):
        
        if config is None:
            # inherit config from WebappServer
            config = WebappServer._config_

        # set default config for single instance
        # self.pgconfig: dict = config["postgres"] #? cli options
        self.project: str = config["database_project"]

        self.restapi = {
            #NOTE: methods are uppercased
            "GET": self._edgeql_SELECT,
            "POST": self._edgeql_INSERT,
            "PATCH": self._edgeql_UPDATE,
            # "PUT": self.edgeQL_REPLACE,
            # "DELETE": self.edgeQL_DELETE
        }

    def connect(self,settings={}):
        
        from gel import create_client # [LocalImport]
        assert isinstance(settings,dict)

        #FIXME: set default settings as kwargs
        kwargs = dict()
        kwargs.update(settings)

        os.chdir(self.project)
        self.client = create_client(**kwargs)
        self.client.ensure_connected()

        return self.client
    
    def edgeql(self,query:str,client=None) -> tuple:
    
        if client is None:
            client = self.client

        # return result as tuple (status, value)
        return "Ok", client.query(query)

    def _edgeql_SELECT(self,d:dict,client=None) -> tuple:
        
        if client is None:
            client = self.client

        query = client.query(f"""
            select {d['table']};
        """)

        # return result as tuple (status, value)
        return "Ok", query

    def _edgeql_INSERT(self,d:dict,client=None) -> tuple:

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

    def _edgeql_UPDATE(self,d:dict,client=None) -> tuple:

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

    def __init__(self, urlpath: str, datasystem):
        super().__init__(urlpath,datasystem)

        self.endpoints["websocket"].update({
            # "ws.reql": self._ws_ReQL,
            "ws.edgeql": self._ws_EdgeQL
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


class WebappServer(Unit):

    def __init__(self, config:BaseConfig):
        
        self.data = []
        self.config = config
        self.middleware = [] #FIXME

        # allow testing python apps
        self.PythonAppType = AsgiLifespanRouter

        # keep current app config available 
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

        return self.PythonAppType(
            routes = routes,
            debug = BaseConfig.debug,
            middleware = self.middleware )

    def set_service(self, unit=False):

        pyconf = self.config["python_app"]
        pyfile = Path(pyconf['path'])/f"{pyconf['module']}.py"

        pyfile.parent.mkdir(parents=True,exist_ok=True) #FIXME
        pyfile.write_text(self.generate_python_script(pyconf))

        if unit is True:
            # force new NginxUnit config
            self.load_unit_config(source="json")
            self.set_unit_config(share_directory=True)
            Unit.put_unit_config()

    @staticmethod
    def generate_python_script(pyconf:dict):

        return f"""# --- start Python3 script --- #

# Information:
# auto-generated by sweetheart.services.WebappServer
# [ USER: {os.getuser()} ] [ DATE: {os.stdout("date")} ]

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
# NOTE: Sweetheart aims to serve statics directly via NginxUnit, not Asgi/3

{pyconf["callable"]} = WebappServer(config).app(
    # DataHub("/tsdata", TimescaleDB()), # NotImplemented
    DataHub("/geldata", PostgresUnchained()),
)

# --- end of script --- #"""
