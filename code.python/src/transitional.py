
from sweetheart.subprocess import os
from sweetheart.urllib import urlget
from platform import python_version_tuple, freedesktop_os_release


def init_sources():
    # tested on Ubuntu 22.04 LTS

    os.run("sudo apt update && sudo apt upgrade -y")
    #NOTE: update is required here for running into GCP

    # get distro infos
    os_release = freedesktop_os_release()
    distrib = os_release['ID'].lower()
    distbase = os_release['ID_LIKE'].lower()
    try: codename = os_release['UBUNTU_CODENAME'].lower()
    except: raise NotImplementedError("UBUNTU_CODENAME not found in /etc/os-release")

    if not os.stdout("apt policy unit"):

        os.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/nginx-keyring.gpg"],
            input=urlget("https://unit.nginx.org/keys/nginx-keyring.gpg"))

        os.run(["sudo","tee","/etc/apt/sources.list.d/unit.list"],text=True,
            input=f"deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]\
                https://packages.nginx.org/unit/{distrib}/ {codename} unit")

    if not os.stdout("apt policy rethinkdb"):

        op.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/rethinkdb-archive-keyrings.gpg"],
            input=urlget("https://download.rethinkdb.com/repository/raw/pubkey.gpg"))

        os.run(["sudo","tee","/etc/apt/sources.list.d/rethinkdb.list"],text=True,
            input=f"deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]\
                https://download.rethinkdb.com/repository/{distrib}-{codename} {codename} main")

    os.run("sudo apt update",stdout=os.DEVNULL)


def init_project(project:str,libs:dict):

    HOME = os.expanduser("~")

    install = libs.get("apt",[])
    version = '.'.join(python_version_tuple()[:2])

    if not os.which("node"): install.append("nodejs")
    # if not os.which("cargo"): install.append("cargo")
    if not os.which("unitd"): install.append(["unit","unit-python{version}"])
    if not os.which("rethinkdb"): install.append("rethinkdb")

    if install: os.run(["sudo","apt","install",*install])

    if not os.isfile(f"{HOME}/.local/bin/poetry"):
        os.run("curl -sSL https://install.python-poetry.org | python3 -")

    os.makedirs(f"{HOME}/.sweet/{project}/application/typescript/",exist_ok=True)
    os.makedirs(f"{HOME}/.sweet/{project}/configuration/",exist_ok=True)
    os.makedirs(f"{HOME}/.sweet/{project}/documentation/",exist_ok=True)
    
    os.makedirs(f"{HOME}/.sweet/{project}/my_code/python",exist_ok=True)
    try: os.symlink(f"{HOME}/.sweet//{project}/application/typescript/",f"{HOME}/.sweet/{project}/my_code/react")
    except: print(f"link {HOME}/.sweet/{project}/my_code/react already exists")

    if libs.get("npm"):
        #NOTE: npm is installed with nodejs
        cwd = f"{HOME}/.sweet/{project}/application"
        os.run("npm init -y",cwd=cwd)
        os.run(["npm","install",*libs["npm"]],cwd=cwd)

    if libs.get("pip"):
        #NOTE: poetry is used here instead of pip
        cwd = f"{HOME}/.sweet/{project}/my_code/python"
        os.run(f"poetry init -C {cwd} -n --no-ansi --name={project}")
        os.run(["poetry","-C",cwd,"--no-ansi","add",*libs["pip"]])

    if libs.get("cargo"):
        raise NotImplementedError("cargo not implemented yet")
