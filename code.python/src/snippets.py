
import json
import configparser
from datetime import datetime

from sweetheart.subprocess import os
from sweetheart import BaseConfig, echo, verbose, ansi


class Unit: 

    unitconf = {}

    @classmethod
    def set_app_config(cls,config:BaseConfig):

        with open(f"{config.root}/configuration/unit.json") as file_in:
            cls.unitconf.update(json.load(file_in))

        cls.unitconf["applications"]["python_app"].update({
            # set unit config for python application
            "path": config.path_pymodule,
            "home": config.python_env,
            "module": config.python_app_module,
            "callable": config.python_app_callable,
            "group": config.unit_app_user, #FIXME
            "user": config.unit_app_user })
        
        cls.unitconf["routes"]["sweetheart"][-1]["action"].update({
            # set unit config for sharing statics
            "share": f"{config.shared_app_content}$uri",
            "chroot": config.shared_app_content,
            "index": config.shared_app_index })
    
    @classmethod
    def put_unit_config(cls):

        # fixed settings
        unithost = "http://localhost"
        unitsocket = "/var/run/control.unit.sock"

        assert cls.unitconf["listeners"]
        assert cls.unitconf["routes"]["sweetheart"]
        assert cls.unitconf["applications"]["python_app"]

        echo("configuring Nginx Unit ...")
        verbose("unit config:",cls.unitconf,level=2)

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            json.dump(cls.unitconf,tempfile)
            tempname = tempfile.name

        stdout = eval(os.stdout( ["sudo",
            "curl","-X","PUT","-d",f"@{tempname}",
            "--unix-socket",unitsocket,f"{unithost}/config/"] ))

        os.remove(tempname)
        assert isinstance(stdout,dict)
        
        verbose("set unit:",
            ansi.GREEN, stdout.get('success',''),
            ansi.RED, stdout.get('error',''),
            level=0 )

        if stdout.get('success'):
            os.run("sudo systemctl reload-or-restart unit")


class Systemd:

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

        os.run(["sudo","cp",tempname,f"/etc/systemd/system/{service}.service"])
        os.run(["sudo","systemctl","enable",service])

        os.remove(tempname)


class Datahub: #FIXME

    # schemes = ("http","ws")
    data = {"status":"test-init"}
        
    async def endpoint(self,scope,receive,send):

        # provide a default etag
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
