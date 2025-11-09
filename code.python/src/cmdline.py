"""
Command Line Interface for Sweetheart
"""

import argparse
from sweetheart import *
from sweetheart import __version__


class CommandLineInterface:

    def __init__(self) :

        """ build Command Line Interface with more readable code
            it uses argparse but provides better look and feel """        

        # provide default parsers tools
        self.parser= argparse.ArgumentParser()
        self.subparser= self.parser.add_subparsers()
        self.REMAINDER= argparse.REMAINDER
        self.SUPPRESS= argparse.SUPPRESS
        self.dict= { "_": self.parser }
        self.cur= "_"
    
    def opt(self,*args,**kwargs):
        self.dict[self.cur].add_argument(*args,**kwargs)

    def sub(self,*args,**kwargs):
        self.cur = args[0]
        self.dict[args[0]] = self.subparser.add_parser(*args,**kwargs)
    
    def set_function(self,func):
        """ set related function for the current parser or subparser """
        self.dict[self.cur].set_defaults(func=func)

    def set_parser(self):
        self.args = self.parser.parse_args()
        return self.args

    def apply_function(self,**kwargs):
        """ apply related function defined with set_function """
        self.args.func(self.args,**kwargs)


if __name__ == "__main__": 

    # Set Sweetheart Command Line Interface

    cli = CommandLineInterface()

    #! set default function of command line interface
    cli.set_function( lambda args: print(
        f"{ansi.PINK}Welcome to the Sweetheart command line",
        f"use 'init' for starting up, '--help' for getting help{ansi.NULL}",sep="\n"))

    cli.opt("-V","--version",action="version",
        version=f"{ansi.PINK}Sweetheart {__version__}{ansi.NULL}",
        help="provide the version info of sweetheart")

    cli.opt("-v","--verbose",action="count",default=0,
        help="get additional messages about ongoing process")

    cli.opt("-p",dest="project",nargs=1,default=BaseConfig.master_project,
        help="set a project name different from the default one")


    def _command_init(args):

        if args.package:
            raise NotImplementedError
        else: 
            # [LocalImport]
            from sweetheart.transitional import ProjectSweetheart
            ProjectSweetheart.initdev()

    # set init command
    cli.sub("init",help="launch init process setting up new project")
    cli.opt("package",nargs=cli.REMAINDER,help="additional resources to install")
    cli.set_function(_command_init)


    def _command_build(args):

        # set project config
        project = args.project or BaseConfig.master_project
        config = set_config(project=project)

        #set directories
        cache = f"{config.root}/.build-cache"
        chroot = config["shared_content"]["chroot"]

        assert os.isfile(f"package.json"),\
            "missing package.json file in current directory"

        # build app with parceljs
        echo("build webapp from current dir:",chroot)
        os.run(["npx","parcel","build","--cache-dir",cache,"--dist-dir",chroot])

    # set build command
    cli.sub("build",help="build your project webapp using parceljs")
    cli.set_function(_command_build)


    # --- Execute Sweetheart Command Line Arguments ---
    # process given arguments and apply the related function

    argv = cli.set_parser()
    BaseConfig.verbosity = getattr(argv,"verbose",BaseConfig.verbosity)
    cli.apply_function()