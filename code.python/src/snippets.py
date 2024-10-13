
import json
import configparser
from datetime import datetime

from sweetheart.subprocess import os
from sweetheart.asgi3 import JSONResponse, Websocket
from sweetheart import BaseConfig, echo, verbose, ansi


class Unit: 

    unitconf = {
        "listeners": {},
        "routes": {"sweetheart": [{}, {"action":{}} ]},
        "applications": {"python_app": {}} }

    unithost = "http://localhost"
    unitlog = "/var/log/unit.log"
    unitsocket = "/var/run/control.unit.sock"

    def load_unit_config(self,source:str):

        assert hasattr(self,"config")
        assert isinstance(self.config,BaseConfig)

        if source == "json":
            # load unit config from json config file
            #NOTE: induces reset of current unit config afterwards
            with open(f"{self.config.root}/configuration/unit.json") as file_in:
                Unit.unitconf = json.load(file_in)

        elif source == "current":
            # load unit current config through unit api
            #NOTE: allows updating current unit config
            raise NotImplementedError
        
        else:
            raise ValueError

    def set_unit_config(
        self,
        settings = {},
        share_directory = False ):

        #NOTE: this currently manages only 1 python app

        assert hasattr(self,"config")
        assert isinstance(self.config,BaseConfig)
        
        for key in settings.keys():

            # update python app settings if given
            if key in self.config["python_app"]:
                self.config["python_app"][key] = settings[key]

            # update shared content settings if given
            elif key in self.config["shared_content"]:
                self.config["shared_content"][key] = settings[key]

            else: raise KeyError

        #! set python env for setting Nginx Unit
        self.config["python_app"]["home"] = self.config.python_env
        
        # set python app from existing config
        Unit.unitconf["applications"]["python_app"].update(
            self.config["python_app"])
        
        if share_directory and self.config["shared_content"]["share"][-4:] != "$uri":
            #! expose full content of given path
            self.config["shared_content"]["share"] += "$uri"

        # set a direct acces to shared content as statics
        Unit.unitconf["routes"]["sweetheart"][-1]["action"].update(
            self.config["shared_content"])
        
    @classmethod
    def put_unit_config(cls):

        assert cls.unitconf["listeners"]
        assert cls.unitconf["applications"]["python_app"]
        assert cls.unitconf["routes"]["sweetheart"][-1]["action"]

        echo("configuring Nginx Unit ...")
        verbose("set unit config:",cls.unitconf,level=2)

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            json.dump(cls.unitconf,tempfile)
            tempname = tempfile.name

        stdout = eval(os.stdout(["sudo", "--stdin",
            "curl", "-X", "PUT", "-d", f"@{tempname}",
            "--unix-socket", cls.unitsocket, f"{cls.unithost}/config/"],
            check=True, **os.sudopass() ))

        os.remove(tempname)
        assert isinstance(stdout,dict)
        
        verbose("put unit config:",
            ansi.GREEN, stdout.get('success',''),
            ansi.RED, stdout.get('error',''),
            level=0 )

        if stdout.get('success'): os.run(
            "sudo systemctl reload-or-restart unit",
            check=True )

        if BaseConfig.debug:
            verbose("last unit log messages:",level=0)
            os.run(["sudo","tail",cls.unitlog])


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


class DataHub: #FIXME

    """ abstraction for exchanging JSON data 
        using the http and websocket protocols """

    def __init__(self):

        self.websocket = Websocket()

        # set default callables to catch events
        # this could be changed by instances of DataHub
        self.http_responder = self.on_test
        self.websocket.receiver = self.on_message
        
    async def endpoint(self,scope,receive,send):

        if scope["type"] == "websocket":
            # redirect to the asgi websocket handler
            await self.websocket(self,scope,receive,send)
        
        elif scope["type"] == "http":
            # implement http requests utilities 

            request = await receive()
            # body = request.get("body",b"").decode()

            match scope.headers.get("x-sweetheart-action"):

                case "fetch.init":
                    assert scope["method"] == "head"
                    assert request["type"] == "http.request"
                    response = self.http_responder(data={})
            
            # at end, call response as an asgi app
            await response(scope,receive,send)

    def on_test(self,data):
        return JSONResponse(
            content = { "test": "Welcome!" },
            headers = { "etag": hash(datetime.now()) })

    def on_request(self,data) -> JSONResponse:
        """ handle http request event """
        raise NotImplementedError

    def on_message(self,data):
        """ handle websocket message event """
        raise NotImplementedError
