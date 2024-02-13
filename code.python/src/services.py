

from sweetheart import *
from sweetheart.snippets import *


class HttpServer(xWebsocket):

    def __init__(self,config:BaseConfig):
        
        self._mounted_ = False
        self.config = config
        self.data = []

    def mount(self,*args:Route|Mount):
        """ mount given Route(s) and set facilities from config """

        # ensure mount() call only once
        assert self._mounted_ is False

        # # set the app's working directory
        # os.chdir(self.config["path_webapp"])
        # verbose("mount webapp:",self.config["path_webapp"])

        #NOTE: assumes that args are Route objects
        self.data.extend(args)

        # mount static files given within config
        self.data.extend([Route(relpath,FileResponse(srcpath))\
            for relpath,srcpath in self.config["static_files"].items()])

        # mount static directories given within config
        self.data.extend([Mount(relpath,StaticFiles(directory=srcpath))\
            for relpath,srcpath in self.config["static_dirs"].items()])

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
            self.mount_str_ = ",\n".join(self.args)

        elif args_are((Route,Mount)):
            self.mount(*args)
        
        else:
            raise Exception("Invalid arguments given to app()")
        
        return self.starlette

    def set_service(self,put_config=False,update_unit=False):

        try: unit = BaseConfig.unit
        except: unit = BaseConfig.unit = NginxUnit()

        # set python script for Unit socket
        pyscript = f'''
"""
{ self.config.python_app_script }.py
auto-generated using sweetheart.services.HttpServer
USER: { os.getuser() } DATE: { os.stdout("date") }
"""
from sweetheart.services import *

config = set_config({{  

    # authorized access settings:

    # html templates rendering settings:

    }})

{ self.config.python_app_script } = HttpServer(config).app(
    # set here url routing of your sweetheart app
    { self.mount_str_ } ) '''

        #FIXME: set nginx unit server
        if update_unit: unit.load_config()
        unit.config = self.config
        unit.add_webapp(pyscript)
        del unit.config
        if put_config: unit.put_config()


class NginxUnit(UserDict):        

    def __init__(self):

        self.default_type = "python 3.8"
        self.socket = "/var/run/control.unit.sock"
        self.host,self.port = "http://localhost",80
        verbose("nginx unit host, port:",self.host,self.port)
        self.conffile = f"{BaseConfig.root}/configuration/unit.json"
        
        self.data = {
            "listeners": {
                f"*:{self.port}": {
                    "pass": "routes" } },
            "routes": [],
            "applications": {} }

    # def add_proxy(self,route:str,target:str):

    #     self["routes"].insert(0,
    #         {
    #             "match": {
    #                 "uri": f"{route}"
    #             },
    #             "action": {
    #                 "proxy": target
    #             }
    #         })

    def add_webapp(self,script:str=None,match:str=None):
        
        """ autoset configured starlette webapp within unit config
        this provides a simple way for only one application setting 
        in other cases unit config has to be lead as follow
        see https://unit.nginx.org/howto/starlette/ for details """

        assert hasattr(self,"config")

        if script:
            #FIXME: write a new script for starting app
            os.chdir(self.config.path_pymodule)
            with open(self.config.app_module+'.py','w') as file_out:
                file_out.write(script.strip())

        # set routes section with new app
        route = {
            "action": {
                "pass": f"applications/{self.config.unit_app_name}" }}

        if match:
            route.update({
                "match": {
                    "uri": f"{match}/*" } })
            
        self["routes"].append(route)

        # define related applications section
        self["applications"].update(
            { self.config.unit_app_name: {
                "type": self.default_type,
                "path": self.config.path_pymodule,
                "home": self._.python_env,#FIXME:
                "module": self.config.python_app_module,
                "callable": self.config.python_app_callable,
                "user": self.config.unit_app_user } })

    def load_config(self) -> dict :

        # get current unit config as a dict
        json = eval(os.stdout(
            ["sudo","curl","--unix-socket",self.socket,f"{self.host}/config/"]
            )); assert isinstance(json,dict)

        if json.get('listeners'):
            # update with existing unit config
            verbose("load existing unit config:",json)
            self.update(json)
        else:
            # exiting unit config missing
            echo("INFO: enforce setting new unit config")

        return self

    def put_config(self) -> dict :

        # ensure no missing data
        assert self['listeners'] != {}
        assert self['routes'] != []
        assert self['applications'] != {}

        # write current unit config
        with open(self.tempfile,'w') as file_out:
            json.dump(self.data,file_out,indent=4)

        # put config and restart unit
            
        stdout = eval(os.stdout(
            ["sudo","curl","-X","PUT","-d",f"@{self.tempfile}","--unix-socket",self.socket,f"{self.host}/config/"]
            )); assert isinstance(stdout,dict)
        
        verbose("unit:",stdout.get('success',''),stdout.get('error',''))
        os.run(["sudo","systemctl","reload-or-restart","unit"])

        return stdout
    