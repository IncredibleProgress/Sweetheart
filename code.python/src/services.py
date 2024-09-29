from typing import Self
from collections import UserList

from sweetheart import *
from sweetheart.pythonsys import urllib
from sweetheart.snippets import Unit, Systemd, DataHub
from sweetheart.asgi3 import AsgiLifespanRouter, Route


class WebappServer(Unit):

    def __init__(self,config:BaseConfig):
        
        self.data = []
        self.config = config
        self.middelware = None #FIXME

    def mount(self,*args:str|Route) -> Self:

        def args_are(typ):
            # return True when all args are instances of typ
            return all([isinstance(arg, typ) for arg in args])

        if args_are(str):
            assert not self.data
            assert not hasattr(self,"mount_str_")
            self.mount_str_ = ",\n".join(args)

        elif args_are((Route,)):
            assert not hasattr(self,"mount_str_")
            self.data.extend(args)
        
        else:
            raise Exception("Invalid args given to mount()")

        return self

    def app(self,*args:Route) -> AsgiLifespanRouter:

        self.mount(*args)

        return AsgiLifespanRouter(
            routes = self.data,
            debug = BaseConfig.debug,
            middelware = self.middelware )

    def set_service(self,unitconf=False):

        assert hasattr(self,"mount_str_")
        path = self.config.path_pymodule
        module = self.config.python_app_module

        with open(f"{path}/{module}.py",'w') as python_script:
            python_script.write(f'''
"""
{self.config.python_app_module}.py
auto-generated by sweetheart.services.WebappServer
[USER: {os.getuser()} ] [DATE: {os.stdout("date")} ]
"""
from sweetheart.services import *

config = set_config()

{self.config.python_app_callable} = WebappServer(config).app(
    # set here url routing of your sweetheart app
    {self.mount_str_} )
'''.strip() )
        
        if unitconf:
            # set the Nginx Unit config for app
            Unit.set_unit_config(self.config)
            Unit.put_unit_config()


class RethinkDB(Systemd):

    def __init__(self,config:BaseConfig):
        
        self.config = config
        parsed_url = urllib.parse(config.database_server)

        # set url attributes
        self.scheme = parsed_url.scheme
        self.host = parsed_url.hostname
        self.port = parsed_url.port

    def set_client(self,dbname:str=None):

        # [LocalImport]
        from rethinkdb import r

        if hasattr(self,'conn'):
            echo("existing RethinkDB connection closed",prefix=ansi.RED)
            self.conn.close()

        if dbname is None:
            dbname= self.config.db_name

        self.dbname = dbname
        self.client = self.r = r
        self.conn = r.connect(self.host,self.port,db=dbname)

        return self.client

    def set_service(self,enable:str=None):

        dirpth = self.config.path_database
        adport = urllib.parse(self.config.database_admin).port

        self.set_systemd_service({

            "Unit": {
                "Description": "RethinkDB running for Sweetheart",
                "After": "network.target" },

            "Service": {
                "ExecStart": f"rethinkdb --http-port {adport} -d {dirpth}",
                "Restart": "always",
                "StandardOutput": "syslog",
                "StandardError": "syslog",
                "SyslogIdentifier": "sweetheart-rdb",
                "User": os.getuser(),
                "Group": os.getuser() },#FIXME

            "Install": {
                "WantedBy": "multi-user.target" } })
        
        if enable:
            self.enable_systemd_service(enable)

    # def on_receive(self,websocket,data):
    #     raise NotImplementedError

    def __del__(self):

        if hasattr(self,'conn'):
            # close last RethinkDB connection
            self.conn.close()
    