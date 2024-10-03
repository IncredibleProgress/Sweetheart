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
    basedir = "Sweetheart/applications"
    
    def __init__(self,project:str=master_module):

        home = os.expanduser('~')
        self.root = f"{home}/{BaseConfig.basedir}/{project}"
        self.conffile = f"{self.root}/configuration/config.json"

        self.data = {

            # editable hosts, ports setup
            "database_path": f"{self.root}/databases/rethinkdb-tests",
            "database_server": "rethinkdb://127.0.0.1:28015",
            "database_admin": "http://127.0.0.1:8082",

            # editable unit python app 
            # "unit_app_name": "python_app",#! update with unit.json

            # editable python app settings
            "python_app": {
                # "home": "__undefined__",
                "path": f"{self.root}/my_code/python",
                "module": "start",
                "callable": "webapp",
                "user": os.getuser(),
                "group": os.getuser() },#FIXME
            
            # editable react app settings
            "shared_content": {
                "chroot": self.root,
                "share": f"{self.root}/application/webapp-dist",
                "index": "startpage.html" },
        }
    
    def __getattr__(self,attr):

        """ search non-existing attribute into self.data allowing that
            config.python_bin can be used instead of config['python_bin'] """

        if attr=="python_env" and not self.__dict__.get(attr)\
        or attr=="python_bin" and not self.__dict__.get(attr):

            # autoset the python virtual env
            cwd = self["python_app"]["path"]
            self.python_env= os.stdout(["poetry","env","info","--path","-C",cwd])
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
        init = prefix + f"{level}*" if level != 0 else " *"
        print(init,*args,ansi.NULL)
