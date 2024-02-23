import os as _os_
import shlex as _shlex_
import shutil as _shutil_
# import getpass as _getpass_
import tempfile as _tempfile_
import subprocess as _subprocess_
# import multiprocessing as _multiprocessing_

from pathlib import Path
# from contextlib import contextmanager
from locale import _get_locale_encoding
assert _get_locale_encoding() == "UTF-8"


class os:

    """ reimplements common tools of the python os module
        and extends it with some foreign facilities for ease """

    # env = environ = _os_.environ
    getenv = _os_.getenv
    putenv = _os_.putenv

    getcwd = _os_.getcwd
    # getuser = _getpass_.getuser
    # getpass = _getpass_.getpass
    get_exec_path = _os_.get_exec_path
    # getlocale = _locale_.getlocale

    path = _os_.path
    isdir = _os_.path.isdir
    isfile = _os_.path.isfile
    islink = _os_.path.islink
    expanduser = _os_.path.expanduser

    chdir = _os_.chdir
    mkdir = _os_.mkdir
    makedirs = _os_.makedirs
    symlink = _os_.symlink
    remove = _os_.remove
    rmtree = _shutil_.rmtree
    listdir = _os_.listdir
    # walk = _os_.walk

    # provide distro infos
    # os_release = platform.freedesktop_os_release()
    # distrib = os_release['ID'].lower()
    # distbase = os_release['ID_LIKE'].lower()
    # codename = os_release.get('UBUNTU_CODENAME').lower()

    # temporary files features
    NamedTemporaryFile = _tempfile_.NamedTemporaryFile

    # multiprocessing features
    # Process = _multiprocessing_.Process

    # shell-like features
    which = _shutil_.which
    DEVNULL = _subprocess_.DEVNULL

    @staticmethod
    def run(*args,**kwargs) -> _subprocess_.CompletedProcess[str] :

        """ securized subprocess.run() function with shell=True forbidden
            this intends to protect code against shell injection attacks """

        if kwargs.get('shell'):
            raise Exception("running shell is not allowed")
        
        elif len(args)==1 and isinstance(args[0],str):
            # split given str but doesn't pass shell=True
            args_: list[str] = _shlex_.split(args[0])
            assert "sudo" not in args
            return _subprocess_.run(args_,**kwargs)
        
        elif len(args)==1 and isinstance(args[0],list):
            return _subprocess_.run(args[0],**kwargs)
        
        else:
            raise Exception("invalid arguments given to os.run()")
    
    @staticmethod
    def stdout(*args,**kwargs) -> str :

        return os.run(*args,
            text=True, capture_output=True,
            **kwargs ).stdout.strip()
