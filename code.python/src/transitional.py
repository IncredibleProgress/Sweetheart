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
        "npm":
            ["typescript","parcel","tailwindcss","preact",
            "react","react-dom","@types/react","@types/react-dom"] })


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

    if libs.get("librust"):
        #FIXME: install rust crates from ubuntu/debian packages
        install.extend([ f"librust-{lib.replace('_', '-')}-dev" for lib in libs["librust"] ])

    if install:
        os.run(["sudo","apt-get","install",*install])

    os.makedirs(f"{BASEDIR}/application/typescript/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/configuration/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/documentation/",exist_ok=True)
    os.makedirs(f"{BASEDIR}/my_code/python",exist_ok=True)

    try:
        os.symlink(f"{BASEDIR}/application/typescript/",
            f"{BASEDIR}/my_code/react")
    except Exception as err:
        print(err)

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


# def init_sources():
#     # tested on Ubuntu 22.04 LTS

#     os.run("sudo apt update -qq && sudo apt upgrade -q -y")

#     # get distro infos
#     os_release = freedesktop_os_release()
#     distrib = os_release['ID'].lower()

#     try:
#         codename = os_release['UBUNTU_CODENAME'].lower()
#     except:
#         raise NotImplementedError("UBUNTU_CODENAME not found in /etc/os-release")

#     if not os.stdout("apt policy unit"): #FIXME

#         os.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/nginx-keyring.gpg"],
#             input=urlget("https://unit.nginx.org/keys/nginx-keyring.gpg"))

#         os.run(["sudo","tee","/etc/apt/sources.list.d/unit.list"],text=True,
#             input=f"deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]\
#                 https://packages.nginx.org/unit/{distrib}/ {codename} unit")

#     if not os.stdout("apt policy rethinkdb"): #FIXME

#         op.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/rethinkdb-archive-keyrings.gpg"],
#             input=urlget("https://download.rethinkdb.com/repository/raw/pubkey.gpg"))

#         os.run(["sudo","tee","/etc/apt/sources.list.d/rethinkdb.list"],text=True,
#             input=f"deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]\
#                 https://download.rethinkdb.com/repository/{distrib}-{codename} {codename} main")

#     os.run("sudo apt update -qq") #FIXME
