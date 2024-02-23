

from sweetheart import *
from sweetheart.snippets import *


class HttpServer(xWebsocket):

    def __init__(self,config:BaseConfig):
        
        self.data = []
        self.config = config
        self._mounted_ = False

    def mount(self,*args:Route|Mount):
        """ mount given Route(s) and set facilities from config """

        # ensure mount() call only once
        assert self._mounted_ is False

        #NOTE: assumes that args are Route objects
        self.data.extend(args)

        # set the webapp Starlette object
        self.starlette = Starlette(routes=self.data)
        self._mounted_ = True

        return self

    def app(self,*args:str|Route|Mount) -> Starlette:
        """ mount(*args) and return related Starlette object """

        args_are = lambda typ:\
            all([ isinstance(arg,typ) for arg in args ])

        if args_are(str):
            self.mount([ eval(str) for str in args ])
            self.mount_str_ = ",\n".join(args)

        elif args_are((Route,Mount)):
            self.mount(*args)
        
        else:
            raise Exception("Invalid arguments given to app()")
        
        return self.starlette

    def set_service(self,put_config=False):

        cf= self.config
        startfile= f"{cf.path_pymodule}/{cf.python_app_module}.py"

        with open(startfile,'w') as file_out:
            file_out.write(f'''
"""
{self.config.python_app_module}.py
auto-generated using sweetheart.services.HttpServer
USER: {os.getuser()} DATE: {os.stdout("date")}
"""
from sweetheart.services import *

config = set_config({})

{self.config.python_app_callable} = HttpServer(config).app(
    # set here url routing of your sweetheart app
    {self.mount_str_} ) ''')

        # set nginx unit server
        unit = NginxUnit()
        unit.set_app_config(self.config)
        if put_config: unit.put_config()


class NginxUnit(UserDict):        

    def __init__(self) :

        self.data = {}
        self.host = "http://localhost"
        self.socket = "/var/run/control.unit.sock"

    def set_app_config(self,config:BaseConfig):

        self.unitconf = f"{config.root}/configuration/unit.json"

        with open(self.unitconf) as file_in:
            self.update(json.load(file_in))

        try:
            app = self["applications"][config.unit_app_name]
        except:
            raise Exception("Error, python app not set for unit")
            
        app["path"] = config.path_pymodule
        app["home"] = config.python_env
        app["module"] = config.python_app_module
        app["callable"] = config.python_app_callable
        app["user"] = config.unit_app_user

    def put_config(self) -> dict :

        assert self["listeners"]
        assert self["routes"]
        assert self["applications"]

        verbose("unit config:",self.data,level=2)

        with os.NamedTemporaryFile(delete=False) as tempfile:
            json.dump(self.data,tempfile)
            tempname = tempfile.name

        stdout = eval(os.stdout(
            ["sudo","curl","-X","PUT","-d",f"@{tempname}","--unix-socket",self.socket,f"{self.host}/config/"]
            )); assert isinstance(stdout,dict)

        os.remove(tempname)
        
        verbose("set unit:",stdout.get('success',''),stdout.get('error',''))
        os.run(["sudo","systemctl","reload-or-restart","unit"])
