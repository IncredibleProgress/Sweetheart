import json
import configparser
from pathlib import Path

from sweetheart.subprocess import os
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

        if source == "conffile":
            # load unit config from json config file
            #NOTE: resets any existing unit config

            assert hasattr(self,"config")
            assert isinstance(self.config,BaseConfig)
            assert os.isfile(self.config.unitconf)

            with open(self.config.unitconf) as file_in:
                Unit.unitconf = json.load(file_in)

        elif source == "unitconf":
            #FIXME: load unit current config through unit api

            Unit.unitconf = json.loads( os.stdout([
                "sudo", "--stdin", "curl", "--unix-socket", 
                self.unitsocket, f"{self.unithost}/config/"
            ], check=True, **os.sudopass() ))
        
        else: raise ValueError

    def set_unit_config(self, 
            settings = {}, *,
            share_directory = True ):

        assert hasattr(self,"config")
        assert isinstance(self.config,BaseConfig)

        application = settings.pop("application",self.application)
        type_app = Unit.unitconf["applications"][application]["type"] # e.g. "python 3"

        assert isinstance(application,str),\
            "application name must be given as string"
        
        for key in settings.keys():
            # update python app settings if given
            if key in self.config[application]:
                self.config[application][key] = settings[key]

            # update shared content settings if given
            elif key in self.config["shared_content"]:
                self.config["shared_content"][key] = settings[key]

            else: raise KeyError(f"'{key}' not found in app's config")

        #FIXME: Set python app from existing config:

        if type_app.lower().strip().startswith("python")\
        and self.config[application]["home"] == "{{python_env}}":
            # auto set python home to current python env
            self.config[application]["home"] = self.config.python_env

        assert application in Unit.unitconf["applications"],\
            f"application '{application}' not found in unit config"

        Unit.unitconf["applications"][application].update(
            self.config[application])
        
        # Expose full content of given path:

        if share_directory \
        and self.config["shared_content"]["share"][-4:] != "$uri":
            self.config["shared_content"]["share"] += "$uri"

        # set a direct acces to shared content as statics
        Unit.unitconf["routes"]["sweetheart"][-1]["action"].update(
            self.config["shared_content"])
    
    @classmethod
    def put_unit_config(cls):

        assert cls.unitconf["listeners"]
        assert cls.unitconf["applications"]
        assert cls.unitconf["routes"]["sweetheart"]

        echo("configuring Nginx Unit ...")
        verbose("set unit config:",cls.unitconf,level=2)

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            json.dump(cls.unitconf,tempfile)
            tempname = tempfile.name

        stdout = json.loads( os.stdout([
            "sudo", "--stdin", "curl", "-X", "PUT", "-d", f"@{tempname}",
            "--unix-socket", cls.unitsocket, f"{cls.unithost}/config/"
        ], check=True, **os.sudopass() ))

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

                    'Unit':
                        ('Description','After','Before'),
                    'Service':
                        ('ExecStart','ExecReload','Restart','Type','User','Group',
                        'WorkingDirectory','StandardOutput','StandardError'),
                    'Install':
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

        os.run([ "sudo", "--stdin", "cp", tempname,
            f"/etc/systemd/system/{service}.service" ],
            check=True, text=True, **os.sudopass() )

        os.remove(tempname)
        os.run(["sudo","systemctl","enable",service])

    def remove_systemd_service(self,service:str):
        raise NotImplementedError
  