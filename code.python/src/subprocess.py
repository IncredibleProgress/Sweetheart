
import stat

import os as _os_
import shlex as _shlex_
import shutil as _shutil_
import getpass as _getpass_
import tempfile as _tempfile_
import subprocess as _subprocess_
# import multiprocessing as _multiprocessing_


class os:
    """
    reimplementation of common tools of the python's os module
    but extending it with some foreign facilities for convenience
    and securing subprocess.run() for use within Sweetheart projects
    """

    # env = environ = _os_.environ
    getenv = _os_.getenv
    putenv = _os_.putenv
    unsetenv = _os_.unsetenv
    expanduser = _os_.path.expanduser
    HOME = _os_.path.expanduser("~")

    getcwd = _os_.getcwd
    getuser = _getpass_.getuser
    getpass = _getpass_.getpass
    get_exec_path = _os_.get_exec_path
    # getlocale = _locale_.getlocale
    
    # path = _os_.path
    isdir = _os_.path.isdir
    isfile = _os_.path.isfile
    islink = _os_.path.islink
    exists = _os_.path.exists
    splitext = _os_.path.splitext

    stat = _os_.stat
    chmod = _os_.chmod
    access = _os_.access # user permissions

    chdir = _os_.chdir
    mkdir = _os_.mkdir
    makedirs = _os_.makedirs
    symlink = _os_.symlink
    remove = _os_.remove
    listdir = _os_.listdir
    # walk = _os_.walk

    move = _shutil_.move
    copy = _shutil_.copy
    copytree = _shutil_.copytree
    rmtree = _shutil_.rmtree

    # [Deprecated]
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
    def run(*args:list|str,**kwargs) -> _subprocess_.CompletedProcess[str] :

        """ secured subprocess.run() function with shell=True forbidden
            this intends to protect code against shell injection attacks """

        if kwargs.get("shell"):
            raise Exception("running shell cmd is not allowed")
        
        elif len(args)==1 and isinstance(args[0],str):
            # split given str but doesn't pass shell=True
            args_: list[str] = _shlex_.split(args[0])
            return _subprocess_.run(args_,**kwargs)
        
        elif len(args)==1 and isinstance(args[0],list):
            return _subprocess_.run(args[0],**kwargs)
        
        else:
            raise Exception("Invalid arguments given to run()")
    
    @staticmethod
    def sudopass() -> dict :
        """
        get password and set it at the standard input as a text,
        allows to run sudo command into Jupyter Notebooks as follow :

            os.run([ "sudo", "--stdin", *command ],
                check=True, text=True, **os.sudopass() )

            os.stdout([ "sudo", "--stdin", *command ],
                check=True, **os.sudopass() )

        NOTE:
            text=True is mandatory for using within os.run()
            conversely, it must be skipped using os.stdout() which set it

            check=True is recommended but still optionnal
            when True, python raises error if the subprocess fails

            sudo command being critical, no magic is provided here,
            the nature of subprocess.run() must be understood to be used
            see https://realpython.com/python-subprocess/ for details
        """

        stdin = {}
        returncode = os.run("sudo -n true",stderr=os.DEVNULL).returncode

        if  returncode == 1 :
            stdin.update(dict(
            # provide sudo password at the stdin
            # getpass returns str, which must be handle externally
            input = os.getpass("sudo passwd required: ") ))

        return stdin

    @staticmethod
    def stdout(*args,**kwargs) -> str :

        """ secured subprocess.run() providing stdout as string """

        return os.run(*args,
            text=True, capture_output=True,
            **kwargs ).stdout.strip()