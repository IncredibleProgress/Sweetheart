
from sweetheart import *
from sweetheart.snippets import *


class HttpServer(xUnit,xWebsocket):

    def __init__(self):
        
        self._mounted_ = False
        self.data = []

    def mount(self,*args:Route|Mount) -> HttpServer:
        """ mount given Route(s) and set facilities from config """

        # ensure mount() call only once
        assert self._mounted_ is False

        # set the app's working directory
        os.chdir(self.config["path_webapp"])
        verbose("mount webapp:",self.config["path_webapp"])

        # assumes that args are Route objects
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


    def get_python_script(self):
        return f'''
"""
{ self.config.app_callable }.py
auto-generated using sweetheart.services.HttpServer
USER: { os.getuser() } DATE: { os.stdout("date") }
"""
from sweetheart.services import *

config = set_config({{  

    # authorized access settings:

    # html templates rendering settings:

    }})

{ self.config.app_callable } = HttpServer(config).app(
    # set here url routing of your sweetheart app
    { self.mount_str_ } ) '''


    def set_service(self,put_config=False,update_unit=False):

        unit = self.get_unit()
        if update_unit: unit.load_config()
        unit.add_webapp(self.get_python_script())
        if put_config: unit.put_config()
        
    def enable_service(self,*args,**kwargs):
        raise Exception("not available for HttpServer")
