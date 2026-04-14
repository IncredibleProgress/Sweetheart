"""
Sweetheart
*innovative foundations for business-grade solutions*
"""

__version__ = "0.1.3"

import json, logging
from sweetheart.subprocess import os
from collections import UserDict as _UserDict_


class BaseConfig(_UserDict_):

    debug = True
    verbosity = 1
    master_project = "sweetheart"
    basedir = f".cache/sweetheart-master"
    allowed_env = ("development","sysadmin","production")

    def __init__(self, *,
            project: str = master_project,
            homedir: str|None = None ) -> None:

        assert os.getenv("SWS_OPERATING_STATE") in BaseConfig.allowed_env,\
            f"Invalid environment value SWS_OPERATING_STATE"

        if project == BaseConfig.master_project:
            # set default settings for master project
            homedir = homedir or f"{os.HOME}/My_code"
            self.caddyfile = f"{homedir}/configuration/Caddyfile"
        else:
            homedir = homedir or f"{os.HOME}/{project.capitalize()}"
            self.basedir = str(BaseConfig.basedir).replace("master",project.lower())
            
        self.root = f"{os.HOME}/{self.basedir}"
        self.conffile = f"{homedir}/configuration/config.json"

        self.data = {
        #1. General Settings:
            # empty for now

        #2. Webapp Settings:

            # editable data bindings
            "/geldata": f"{homedir}/database",

            # editable python app settings
            "python_app": {
                "venv": None,# autoset to python_env
                "path": f"{homedir}/python",
                "module": "start",# no .py extension expected
                "callable": "webapp",
                "user": "www-data",#FIXME
                "group": "www-data",#FIXME
                "sysd": "uvicorn.service",
                "uds": "/tmp/sweetheart.sock",
                "uri": "/geldata",
            },
            # editable statics settings
            "shared_content": {
                "index": "startpage.html",
                "fallback": "startpage.html",
                "chroot": f"{self.root}/application",
            },
            # editable statics setting
            # these are put into NginxUnit config
            # "shared_content_ngu": {
            #     "index": "startpage.html",
            #     "chroot": f"{self.root}/application",
            #     "share": f"{self.root}/application$uri",
            #     #NOTE: fallback allows routing by startpage itself
            #     "fallback": {"share": f"{self.root}/application/startpage.html"},
            # },
        }
    
    def __getattr__(self,attr):

        """ search non-existing attribute into self.data allowing that
            config.python_bin can be used instead of config['python_bin'] """

        if attr=="python_env" and not self.__dict__.get(attr)\
        or attr=="python_bin" and not self.__dict__.get(attr):

            #FIXME: autoset the python virtual env
            cwd = self["python_app"]["path"]

            self.python_env=\
                os.stdout(["poetry","env","info","--path","-C",cwd])\
                or os.getenv("SWS_PYTHON_ENV")

            assert self.python_env,\
                "Related python virtual env not found."

            self.python_bin= f"{self.python_env}/bin/python3"
            return self.__dict__.get(attr)

        else:
            return self.data[attr]
    
    def load_json(self,filename:str=None):

        if filename:
            raise NotImplementedError

        with open(self.conffile) as file_in:
            self.update(json.load(file_in))


def set_config(values={},**kwargs) -> BaseConfig:

    config = BaseConfig(**kwargs)

    if os.isfile(config.conffile):
        config.load_json()
        verbose("load config file:",config.conffile)

    elif BaseConfig.debug: 
        verbose(f"configuration file not found: {config.conffile}")

    config.update(values)
    return config


  #############################################################################
 ## logging functions ########################################################
#############################################################################

class ansi:

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    PINK = "\033[0;95m"
    NULL = "\033[0m"
    SWHT = f"{PINK}Sweetheart{NULL}"


logging.basicConfig(
    # filename = f"{BaseConfig.basedir}/sweetheart.log",
    format = f"{ansi.SWHT} - $levelname - $message",
    level = logging.INFO,
    style = "$" )


def echo(*args,prefix="",**kwargs):

    label = BaseConfig.master_project.upper()
    init = prefix + f"[{label}]"
    print(init,*args,ansi.NULL,**kwargs)


def verbose(*args,level=1,prefix=""):

    """ convenient function for verbose messages, 
        'level' set the intended level of verbosity """

    if BaseConfig.verbosity >= level:
        init = prefix + f"{level}*" if level != 0 else " *"
        print(init,*args,ansi.NULL)