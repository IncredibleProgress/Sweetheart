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

    def __init__(self, *,
            project: str = master_project,
            homedir: str|None = None ) -> None:

        if project == BaseConfig.master_project:
            # set default homedir for master project
            homedir = homedir or f"{os.HOME}/My_code"
        else:
            homedir = homedir or f"{os.HOME}/{project.capitalize()}"
            self.basedir = str(BaseConfig.basedir).replace("master",project)
            
        self.root = f"{os.HOME}/{self.basedir}"
        self.conffile = f"{homedir}/configuration/config.json"
        self.unitconf = f"{homedir}/configuration/unit.json"

        self.data = {
        #1. General Settings:

            "database_project": f"{homedir}/database",

        #2. System Services Settings:

            # editable python app settings
            # these are put into NginxUnit config
            "python_app": {
                "home": "{{python_env}}",# auto set
                "path": f"{homedir}/python",
                "module": "start",# no .py extension expected
                "callable": "webapp",
                "user": os.getuser(),#FIXME
                "group": os.getuser(),#FIXME
            },
            # editable statics setting
            # these are put into NginxUnit config
            "shared_content": {
                "index": "startpage.html",
                "chroot": f"{self.root}/application",
                "share": f"{self.root}/application$uri",
                #NOTE: fallback allows routing by startpage itself
                "fallback": {"share": f"{self.root}/application/startpage.html"},
            },
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

    assert os.isfile(config.conffile),\
        f"Configuration file not found: {config.conffile}."

    config.load_json()
    verbose("load config file:",config.conffile)

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
    format = f"$asctime - {ansi.SWHT} - $levelname - $message",
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


class LoggedException(Exception):

    def __init__(self,message):
        
        level = int(BaseConfig.debug)
        verbose(f"logged:{ansi.RED}",message,level=level)
        logging.error(message)
        super().__init__(message)
