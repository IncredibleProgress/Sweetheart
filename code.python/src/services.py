from sweetheart import *
from typing import Self
from pathlib import Path
from rethinkdb import RethinkDB as R
from sweetheart.systemctl import Unit, Systemd

from sweetheart.asgi3 import (
    AsgiLifespanRouter, DataHub, Route, 
    Websocket, JSONResponse, JSONMessage )


class WebappServer(Unit):

    def __init__(self, config: BaseConfig ):
        
        self.data = []
        self.config = config
        self.middelware = None #FIXME

        # keep current app config available 
        WebappServer._config_ = config

    def mount(self, *args: Route|DataHub ) -> Self:

        # unrelevant instances forbidden
        allow = (Route,DataHub)
        assert all([isinstance(arg,allow) for arg in args])
        
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
            middelware = self.middelware )

    def set_service(self, unit=False):

        pyconf = self.config["python_app"]
        pyfile = Path(pyconf['path']) / f"{pyconf['module']}.py"

        pyfile.parent.mkdir(parents=True,exist_ok=True) #FIXME
        pyfile.write_text(self.generate_python_script(pyconf))

        if unit is True:
            # force new NginxUnit config
            self.load_unit_config(source="json")
            self.set_unit_config(share_directory=True)
            Unit.put_unit_config()

    @staticmethod
    def generate_python_script(pyconf:dict):

        return f"""# --- start Python3 script ---

# Information:
# auto-generated by sweetheart.services.WebappServer
# [ USER: {os.getuser()} ][ DATE: {os.stdout("date")} ]

# Import Sweetheart Services:
from sweetheart.services import *

# Set App Configuration:

config = set_config({{
    # set here your own app config when required
    # but please refer to the documentation first
}})

# Set Asgi/3 App Server:

# create here a runable entry point for your data traffic
# the default and recommended is a RetinkDB data driver at url /data
# Note: Sweetheart aims to serve statics directly via NginxUnit, not Asgi/3

{pyconf["callable"]} = WebappServer(config).app(
    # DataHub("/sql-data", PostgreSQL()), #! Unsupported
    DataHub("/data", RethinkDB()) )

# --- end Python3 script ---"""


class RethinkDB(Systemd):

    def __init__(self,
            config: BaseConfig = None ):
        
        if config is None:
            # get config from WebappServer
            config = WebappServer._config_

        self.r = R()
        self.rconfig: dict = config["rethinkdb"]
        #NOTE: rconfig contains rethinkdb cli options

        self.restapi = {
            #NOTE: methods are uppercased
            "GET": self.rql_FILTER,
            "POST": self.rql_INSERT,
            "PATCH": self.rql_UPDATE,
            # "PUT": self.rql_REPLACE,
            # "DELETE": self.rql_DELETE
        }

    def connect(self, options={}):

        """ Start new connection to RethinkDB server,
            options override settings from the app config. """

        kwargs = dict(
            #NOTE: rethinkdb set default db="test"
            host = "localhost",
            port = self.rconfig["driver-port"] )

        kwargs.update(options)
        connect = self.r.connect(**kwargs)

        # keep first connection as the default one
        if not hasattr(self,"conn"): self.conn = connect

        return connect

    def rql_expr(self, query:str, conn=None) -> tuple:
        """ Run any given RethinkDB query. """

        # set default connection
        if not conn: conn = self.conn

        # return result as tuple (status, value)
        return "Ok", self.r.expr(query).run(conn)

    def rql_FILTER(self, d:dict, conn=None) -> tuple:

        # set default connection
        if not conn: conn = self.conn
        # apply Rest Api: GET
        r = self.r.table(d["table"])
        if d.get("filter"): r = r.filter(d["filter"])

        # return result as tuple (status, value)
        return "Ok",list(r.run(conn))

    def rql_INSERT(self, d:dict, conn=None) -> tuple:

        # set default connection
        if not conn: conn = self.conn
        # apply Rest Api: POST
        query = self.r.table(d["table"]).insert(d["row"]).run(conn)

        # return result as tuple (status, value)
        if query["errors"]: return "Err",query["errors"]
        elif query["inserted"]==1: return "Ok",None
        else: return "Err","No data inserted"
            
    def rql_UPDATE(self, d:dict, conn=None) -> tuple:

        # set default connection
        if not conn: conn = self.conn
        # Rest Api: PATCH
        query = self.r.table(d["table"]).get(d["id"])\
            .update({ d["name"]: d["value"] }).run(conn)
            
        # return result as tuple (status, value)
        if query["errors"]: return "Err",query["errors"]
        elif query["replaced"]==1: return "Ok",None
        else: return "Err","No data updated"

    # def def ReQL_REPLACE(self,d:dict):
    #     # Rest Api: PUT
    #     r = self.r.table(d["table"])
    #     r.get(d["id"]).replace(d["data"]).run(self.connect)

    # def ReQL_DELETE(self,d:dict):
    #     # Rest Api DELETE
    #     r = self.r.table(d["table"])
    #     r.get(d["id"]).delete().run(self.connect)

    def set_service(self,enable:str=None):

        ExecStart = " ".join(["rethinkdb",
            *[f"--{k} {v}" for k,v in self.rconfig.items()] ])

        self.set_systemd_service({
            "Unit": {
                "Description": "RethinkDB running for Sweetheart",
                "After": "network.target" },
            "Service": {
                "ExecStart": ExecStart,
                "Restart": "always",
                "User": os.getuser(),#FIXME
                "Group": os.getuser() },#FIXME
                "WorkingDirectory": f"{self.root}/databases",#FIXME
            "Install": {
                "WantedBy": "multi-user.target" } })
        
        if enable is not None:
            assert isinstance(enable,str)
            self.enable_systemd_service(enable)

    def __del__(self):
        """ Close default connection when object is deleted. """
        #NOTE: multiple connections must be managed explicitly
        if hasattr(self,"conn"): self.conn.close()
