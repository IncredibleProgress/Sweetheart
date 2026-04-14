"""
Command Line Interface for Sweetheart
"""

import sys,argparse
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

    cli.opt("-p",dest="project",nargs=1,default=[BaseConfig.master_project],
        help="set a project name different from the default one")


    def _command_init(args):

        # [LocalImport]
        from sweetheart.transitional import \
            SweetheartMaster,SweetheartProject,JupyterNotebook

        if args.server:
            # [LocalImport]
            from sweetheart.systemctl import Caddy
            
            server = Caddy()

        if args.package:
            raise NotImplementedError

        if args.project == ["jupyter"]:
            #FIXME: for testing purposes only
            JupyterNotebook.initdev(project=args.project[0])

        elif args.project != [BaseConfig.master_project]:
            SweetheartProject.initdev(project=args.project[0])
        
        else: 
            SweetheartMaster.initdev()

            # build the default configuration
            config = BaseConfig()
            with open(config.conffile,"w") as file_out:
                json.dump(config.data,file_out,indent=4)
        
    # set init command
    cli.sub("init",help="launch init process setting up new project")
    cli.opt("-s","--server",action="store_true",help="set Caddy web server on this machine")
    cli.opt("package",nargs=cli.REMAINDER,help="additional resources to install")
    cli.set_function(_command_init)


    def _command_build(args):

        # set project config
        config = set_config(project=args.project[0])

        # set directories
        cache = f"{config.root}/.build-cache"
        chroot = config["shared_content"]["chroot"]

        # current directory must be a valid node project
        if not os.isfile("package.json"):
            logging.error(
                f"Missing package.json in {os.getcwd()} "+\
                "which must contain a valid node project.")
            sys.exit(1)

        if not args.skip_js:
            # build app with parceljs
            echo("build webapp in:",chroot)
            os.run(["npx","parcel","build","--cache-dir",cache,"--dist-dir",chroot])

        if args.reload_unit:
            # restart Unit reloading python app script
            echo("restarting Nginx Unit ...",prefix="\n")
            os.run("sudo systemctl reload-or-restart unit")

            if BaseConfig.debug:

                # [LocalImport]
                from sweetheart.systemctl import Unit

                verbose("last unit log messages:",level=0)
                os.run(["sudo","tail",Unit.unitlog])

    # set build command
    cli.sub("build",help="build and run your project webapp")
    cli.opt("-s","--skip-js",action="store_true",help="skip building webapp with parceljs")
    cli.opt("-r","--reload-unit",action="store_true",help="reload Nginx Unit python app")
    cli.set_function(_command_build)


    # --- Execute Sweetheart Command Line Arguments ---
    # process given arguments and apply the related function

    argv = cli.set_parser()
    BaseConfig.verbosity = getattr(argv,"verbose",BaseConfig.verbosity)
    cli.apply_function()