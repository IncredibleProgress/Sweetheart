"""
SWEETHEART 0.1.3 'Reactive'
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
            "path_database": f"{self.root}/database/rethinkdb-tests",
            "path_pymodule": f"{self.root}/my_code/python",# no / at end

            # editable html rendering settings
            "static_files": {},
            "static_dirs": { "/": "/webapp" } }
    
    def load_json(self):
        """ update config from given json file """

        if os.path.isfile(self.conffile):

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
