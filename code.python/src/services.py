

from sweetheart import *
from sweetheart.snippets import *


class WebappServer(xWebsocket):

    def __init__(self,config:BaseConfig):
        
        self.data = []
        self.config = config

    def mount(self,*args:str|Route|Mount):

        args_are: bool = lambda typ:\
            all([ isinstance(arg,typ) for arg in args ])
            # True when all args are instances of typ

        if args_are(str):

            assert not self.data
            assert not hasattr(self,"mount_str_")

            self.mount_str_ = ",\n".join(args)

            try: [ eval(string) for string in args ]
            except: raise Exception("Invalid string given to mount()")

        elif args_are((Route,Mount)):

            assert not hasattr(self,"mount_str_")
            self.data.extend(args)
        
        else:
            raise Exception("Invalid args given to mount()")

        return self

    def app(self,*args:str|Route|Mount) -> Starlette:

        self.mount(*args)

        return Starlette(
            debug = BaseConfig.debug,
            routes = self.data )

    def set_service(self,put_config=False):

        cf = self.config
        start = f"{cf.path_pymodule}/{cf.python_app_module}.py"

        with open(start,'w') as python_script:
            python_script.write(
f'''
"""
{self.config.python_app_module}.py
auto-generated using sweetheart.services.WebappServer
USER: {os.getuser()} DATE: {os.stdout("date")}
"""
from sweetheart.services import *

config = set_config()

{self.config.python_app_callable} = WebappServer(config).app(
    # set here url routing of your sweetheart app
    {self.mount_str_} )
''')
        #FIXME: only for tests
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
            raise Exception("Invalid Unit settings 'applications'")
            
        app.update({
            "path": config.path_pymodule,
            "home": config.python_env,
            "module": config.python_app_module,
            "callable": config.python_app_callable,
            "user": config.unit_app_user })

        try:
            route = self["routes"][-1]["action"]
        except:
            raise Exception("Invalid Unit settings 'routes'")

        route.update({
            "share": f"{config.shared_app_content}$uri",
            "chroot": config.shared_app_content,
            "index": config.shared_app_index })
            
    def put_config(self):

        assert self["listeners"]
        assert self["routes"]
        assert self["applications"]

        echo("configuring NGINX Unit for you ...")
        verbose("unit config:",self.data,level=2)

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            json.dump(self.data,tempfile)
            tempname = tempfile.name

        stdout = eval(os.stdout( ["sudo",
            "curl","-X","PUT","-d",f"@{tempname}",
            "--unix-socket",self.socket,f"{self.host}/config/"]
            )); assert isinstance(stdout,dict)

        os.remove(tempname)
        
        verbose("set unit:",
            ansi.GREEN, stdout.get('success',''),
            ansi.RED, stdout.get('error',''),
            level=0 )

        os.run("sudo systemctl reload-or-restart unit")
