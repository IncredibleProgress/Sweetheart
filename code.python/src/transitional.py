from sweetheart import BaseConfig
from sweetheart.subprocess import os
from platform import python_version_tuple

# ensure Sweetheart runs in a development purpose
assert os.getenv("SWS_OPERATING_STATE") == "development"


def init_sweetheart(system=False):

    init_project("sweetheart", libs= {
        "apt": 
            ["unit",f"unit-python{ '.'.join(python_version_tuple()[:2]) }",
            "rethinkdb","python3-poetry"] if system else [],
        "pip":
            ["rethinkdb","pydantic","ipykernel"],
        # "npm":
        #     ["typescript","parcel","tailwindcss","preact",
        #     "react","react-dom","@types/react","@types/react-dom"]
    })


def init_project(
        project:str,
        libs:dict[str,list[str]] ) -> None :
    """ 
    Create or init a new project for dev

        project: str
            name of the project to initialize
            its related directory will appear into ~/.sweet

        libs: dict[str,list[str]]
            set the requires libraries to install
            {
                "apt": [],
                "librust": [],
                "cargo": [], # Not Implemented
                "pip": [],
                "npm": []
            }
    """

    home = os.expanduser("~")
    BASEDIR = f"{home}/{BaseConfig.basedir}/{project}"
    
    install = libs.get("apt",[])

    if libs.get("librust"): #FIXME
        # install rust crates from ubuntu/debian packages
        install.extend([ f"librust-{ lib.replace('_','-') }-dev" 
            for lib in libs["librust"] ])

    if install:
        os.run(["sudo","apt-get","install",*install])

    os.makedirs(f"{BASEDIR}/databases/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/application/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/configuration/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/documentation/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/my_code/python",exist_ok=True)

    # try:
    #     os.symlink(f"{BASEDIR}/application/typescript/",
    #         f"{BASEDIR}/my_code/react")
    # except Exception as err:
    #     print(err)

    if libs.get("npm"):

        if not os.which("npm"):
            os.run("sudo apt-get install npm")
            
        cwd = f"{BASEDIR}/application"
        os.run("npm init -y",cwd=cwd)
        os.run(["npm","install",*libs["npm"]],cwd=cwd)

    if libs.get("pip"):
        #NOTE: poetry is used here instead of pip

        if not os.which("poetry"):
            os.run("sudo apt-get install python3-poetry")

        cwd = f"{BASEDIR}/my_code/python"
        os.run(f"poetry init -C {cwd} -n --no-ansi --name={project}")
        os.run(["poetry","-C",cwd,"--no-ansi","add",*libs["pip"]])

    if libs.get("cargo"):

        # if not os.which("cargo"):
        #     os.run("sudo apt-get install cargo")

        raise NotImplementedError("cargo not implemented")
