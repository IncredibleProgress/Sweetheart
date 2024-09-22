"""
Sweetheart
innovative foundations for enterprise-grade solutions
"""

__version__ = "0.1.3"

import json
from collections import UserDict
from sweetheart.subprocess import os


class BaseConfig(UserDict):

    debug = True
    verbosity = 1
    master_module = "sweetheart"
    
    def __init__(self,project:str=master_module):

        self.root = f"{os.expanduser('~')}/.sweet/{project}"
        self.conffile = f"{self.root}/configuration/config.json"

        self.data = {

            # editable general settings
            "path_webapp": f"{self.root}/application",
            "path_pymodule": f"{self.root}/my_code/python",#! no / at end
            "path_database": f"{self.root}/databases/rethinkdb-tests",

            # editable hosts, ports setup
            "database_server": "rethinkdb://127.0.0.1:28015",
            "database_admin": "http://127.0.0.1:8082",

            # editable python app settings
            "python_app_module": "start",#! no .py suffix
            "python_app_callable": "webapp",
            "shared_app_content": f"{self.root}/application/webapp-dist",
            "shared_app_index": "startpage.html",
            # "unit_app_name": "python_app",#! update with unit.json
            "unit_app_user": os.getuser(),#! group must exists too
        }
    
    def __getattr__(self,attr):

        """ search non-existing attribute into self.data allowing that
            config.path_webapp can be used instead of config['path_webapp'] """

        if attr=="python_bin" and not self.__dict__.get(attr)\
        or attr=="python_env" and not self.__dict__.get(attr):
            #FIXME: autoset the python virtual env
            cwd = self["path_pymodule"]
            self.python_env= os.stdout(f"poetry env info --path -C {cwd}")
            self.python_bin= f"{self.python_env}/bin/python3"
            return self.__dict__.get(attr)

        else:
            return self.data[attr]
    
    def load_json(self,filename:str=None):

        if filename:
            raise NotImplementedError

        with open(self.conffile) as file_in:
            self.update(json.load(file_in))


def set_config(values={}) -> BaseConfig:

    config = BaseConfig()

    if os.isfile(config.conffile):
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
    PINK = "\033[0;35m"
    NULL = "\033[0m"


def echo(*args,prefix="",**kwargs):

    label = BaseConfig.master_module.upper()
    init = prefix + f"[{label}]"
    print(init,*args,ansi.NULL,**kwargs)


def verbose(*args,level=1,prefix=""):

    """ convenient function for verbose messages, 
        level set the intended level of verbosity """

    if BaseConfig.verbosity >= level:
        init = prefix + f"{level}-" if level != 0 else " -"
        print(init,*args,ansi.NULL)
