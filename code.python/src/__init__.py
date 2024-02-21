"""
SWEETHEART 0.1.3 (React)
"""

import re,sys,json
from collections import UserDict
from sweetheart.subprocess import os


class BaseConfig(UserDict):

    verbosity = 0
    master_module = "sweetheart"
    
    def __init__(self):

        self.root = f"{os.expanduser('~')}/.sweet"
        self.conffile = f"{self.root}/configuration/config.json"

        self.data = {
            # editable general settings
            "path_webapp": f"{self.root}/application",
            "path_database": f"{self.root}/databases/rethinkdb-tests",
            "path_pymodule": f"{self.root}/my_code/python",#! no / at end

            # editable python app settings
            "python_app_module": "start",#! no .py at end
            "python_app_callable": "webapp",
            "unit_app_name": "starlette",
            "unit_app_user": os.getuser(),

            # editable html rendering settings
            # "static_files": {},
            # "static_dirs": { "/": f"webapp" }
            }
    
    def __getattr__(self,attr):
        """ search non-existing attribute into self.data
            config.path_webapp can be used instead of config['path_webapp'] """

        if attr=="python_bin" and not self.__dict__.get(attr)\
        or attr=="python_env" and not self.__dict__.get(attr):
            #FIXME: set the python virtual env
            cwd = self["path_pymodule"]
            self.python_env= os.stdout(f"poetry env info --path -C {cwd}")
            self.python_bin= f"{self.python_env}/bin/python3"
            return self.__dict__.get(attr)

        else:
            return self.data[attr]
    
    def load_json(self):
        """ update config from given json file """

        if os.isfile(self.conffile):

            with open(self.conffile) as file_in:
                self.update(json.load(file_in))
                verbose("load config file:",self.conffile)


  #############################################################################
 ## logging functions ########################################################
#############################################################################

def echo(*args,blank=False):
    """ convenient function for formated prints """

    label = BaseConfig.master_module.upper()
    init = "\n" if blank else ""
    print(init,f"[{label}]",*args)


def verbose(*args,level:int=1):
    """ convenient function for verbose messages 
        level set the intended level of verbosity """

    if BaseConfig.verbosity >= level:
        print(f"swh:{level}:",*args)
