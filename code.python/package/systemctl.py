import json
import configparser
from pathlib import Path

from sweetheart.subprocess import os
from sweetheart import BaseConfig, echo, verbose, ansi


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

            assert section in ('Unit','Service','Install'),\
                "Invalid section in systemd service config"

            for option,value in config[section].items():
                if BaseConfig.debug and option not in {
                    'Unit':
                        ('Description','Documentation','After','Before','Requires'),
                    'Service':
                        ('ExecStart','ExecReload','Restart','Type','User','Group',
                        'WorkingDirectory','StandardOutput','StandardError','TimeoutStopSec',
                        'LimitNOFILE','PrivateTmp','ProtectSystem','AmbientCapabilities'),
                    'Install':
                        ('WantedBy','RequiredBy') }[section]:

                    verbose(f"option '{option}' setting systemd : to check",
                        level=0, prefix=ansi.RED)

                # set option given with config
                self.sysdconf[section][option] = value

    def enable_systemd_service(self,service:str):

        assert os.getenv("SWS_OPERATING_STATE") in ("development","sysadmin"),\
            "systemd services can only be set in development or sysadmin state"

        with os.NamedTemporaryFile("wt",delete=False) as tempfile:
            #NOTE: space_around_delimiters must be set at False
            self.sysdconf.write(tempfile, space_around_delimiters=False )
            tempname = tempfile.name

        assert service.endswith(".service"),\
            "service name must end with '.service' extension"

        os.run([ "sudo", "--stdin", "cp", tempname,
            f"/etc/systemd/system/{service}" ],
            check=True, text=True, **os.sudopass() )

        os.run(["sudo","systemctl","enable",service])

        os.remove(tempname)
        del self.sysdconf

    def remove_systemd_service(self,service:str):
        raise NotImplementedError


class Caddy(Systemd):

    # def set_systemd_service(self):
    #     # set_caddy_service is provided with presets
    #     raise NotImplementedError

    def set_caddy_service(self,caddyfile:str):
        self.set_systemd_service({

            'Unit': dict(
                Description='Caddy web server',
                Documentation='https://caddyserver.com/docs/',
                After='network.target network-online.target',
                Requires='network-online.target' ),

            'Service': dict(
                # Caddy's website recommended settings:
                Type='notify',
                User='www-data',#FIXME
                Group='www-data',#FIXME
                ExecStart=f'caddy run --environ --config {caddyfile}',
                ExecReload=f'caddy reload --config {caddyfile} --force',
                TimeoutStopSec='5s',
                LimitNOFILE='1048576',
                PrivateTmp='true',
                ProtectSystem='full',
                AmbientCapabilities='CAP_NET_ADMIN CAP_NET_BIND_SERVICE',

                #FIXME: Hardened security settings:
                NoNewPrivileges=True,               # prevent privilege escalation
                ProtectKernelTunables=True,         # can't modify kernel params via /proc/sys
                ProtectKernelModules=True,          # can't load kernel modules
                ProtectControlGroups=True,          # can't tamper with cgroups
                RestrictNamespaces=True,            # can't create new namespaces
                RestrictSUIDSGID=True,              # can't execute SUID/GUID binaries
                # LockPersonality=True,               # can't change execution domain
                MemoryDenyWriteExecute=True,        # prevents JIT/shellcode tricks
                SystemCallFilter='@system-service', # whitelist syscalls
                # ProtectHome=True,                   # no access to /home
            ),
            'Install': dict(
                WantedBy='multi-user.target')
        })
    
    def enable_caddy_service(self,service="caddy.service"):
        self.enable_systemd_service(service)


class PythonApp(Systemd):

    def set_uvicorn_service(self,settings:dict):
        self.set_systemd_service({

            'Unit': dict(
                Description='Python web application',
                After='network.target' ),

            'Service': dict(
                User=settings["user"],
                Group=settings["group"],
                WorkingDirectory=settings["path"],
                ExecStart=(
                    f'{settings["home"]}/bin/uvicorn '
                    f'--uds {settings["uds"]} '
                    '--forwarded-allow-ips=127.0.0.1 ' #FIXME
                    '--proxy-headers '             
                    f'{settings["module"]}:{settings["callable"]}' ),
                Restart='always',
                RestartSec='3',

                #FIXME: Hardened security settings:
                NoNewPrivileges='true',
                # ReadWritePaths='/run/uvicorn' 
                # PrivateTmp='true',
                # ProtectSystem='full',
                # CapabilityBoundingSet='CAP_NET_BIND_SERVICE',
                AmbientCapabilities='CAP_NET_BIND_SERVICE' ),

            'Install': dict(
                WantedBy='multi-user.target')
        })

    def enable_uvicorn_service(self,service="uvicorn.service"):
        self.enable_systemd_service(service)


# class Unit: 

#     #NOTE: NginxUnis is not longer supported
#     # https://unit.nginx.org for more details

#     unitconf = {
#         "listeners": {},
#         "routes": {"sweetheart": [{}, {"action":{}} ]},
#         "applications": {"python_app": {}} }

#     unithost = "http://localhost"
#     unitlog = "/var/log/unit.log"
#     unitsocket = "/var/run/control.unit.sock"

#     def load_unit_config(self,source:str):

#         if source == "conffile":
#             # load unit config from json config file
#             #NOTE: resets any existing unit config

#             assert hasattr(self,"config")
#             assert isinstance(self.config,BaseConfig)
#             assert os.isfile(self.config.unitconf)

#             with open(self.config.unitconf) as file_in:
#                 Unit.unitconf = json.load(file_in)

#         elif source == "unitconf":
#             #FIXME: load unit current config through unit api

#             Unit.unitconf = json.loads( os.stdout([
#                 "sudo", "--stdin", "curl", "--unix-socket", 
#                 self.unitsocket, f"{self.unithost}/config/"
#             ], check=True, **os.sudopass() ))
        
#         else: raise ValueError

#     def set_unit_config(self, 
#             settings = {}, *,
#             share_directory = True ):

#         assert hasattr(self,"config")
#         assert isinstance(self.config,BaseConfig)

#         application = settings.pop("application",self.application)
#         type_app = Unit.unitconf["applications"][application]["type"] # e.g. "python 3"

#         assert isinstance(application,str),\
#             "application name must be given as string"
        
#         for key in settings.keys():
#             # update python app settings if given
#             if key in self.config[application]:
#                 self.config[application][key] = settings[key]

#             # update shared content settings if given
#             elif key in self.config["shared_content"]:
#                 self.config["shared_content"][key] = settings[key]

#             else: raise KeyError(f"'{key}' not found in app's config")

#         #FIXME: Set python app from existing config:

#         if type_app.lower().strip().startswith("python")\
#         and self.config[application]["home"] == "{{python_env}}":
#             # auto set python home to current python env
#             self.config[application]["home"] = self.config.python_env

#         assert application in Unit.unitconf["applications"],\
#             f"application '{application}' not found in unit config"

#         Unit.unitconf["applications"][application].update(
#             self.config[application])
        
#         # Expose full content of given path:

#         if share_directory \
#         and self.config["shared_content"]["share"][-4:] != "$uri":
#             self.config["shared_content"]["share"] += "$uri"

#         # set a direct acces to shared content as statics
#         Unit.unitconf["routes"]["sweetheart"][-1]["action"].update(
#             self.config["shared_content"])
    
#     @classmethod
#     def put_unit_config(cls):

#         assert cls.unitconf["listeners"]
#         assert cls.unitconf["applications"]
#         assert cls.unitconf["routes"]["sweetheart"]

#         echo("configuring Nginx Unit ...")
#         verbose("set unit config:",cls.unitconf,level=2)

#         with os.NamedTemporaryFile("wt",delete=False) as tempfile:
#             json.dump(cls.unitconf,tempfile)
#             tempname = tempfile.name

#         stdout = json.loads( os.stdout([
#             "sudo", "--stdin", "curl", "-X", "PUT", "-d", f"@{tempname}",
#             "--unix-socket", cls.unitsocket, f"{cls.unithost}/config/"
#         ], check=True, **os.sudopass() ))

#         os.remove(tempname)
#         assert isinstance(stdout,dict)
        
#         verbose("put unit config:",
#             ansi.GREEN, stdout.get('success',''),
#             ansi.RED, stdout.get('error',''),
#             level=0 )

#         if stdout.get('success'): os.run(
#             "sudo systemctl reload-or-restart unit",
#             check=True )

#         if BaseConfig.debug:
#             verbose("last unit log messages:",level=0)
#             os.run(["sudo","tail",cls.unitlog])