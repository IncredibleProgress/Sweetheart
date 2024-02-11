"""
SWEETHEART 0.1.x 'new age rising'
"""

import re,sys,json
from collections import UserDict
from sweetheart.subprocess import os

class BaseConfig(UserDict):
    
    def __init__(self):

        self.root = f"{os.expanduser('~')}/.sweet"
        self.conffile = f"{self.root}/configuration/config.json"
