import sys,json
from sweetheart.subprocess import os
from platform import python_version_tuple
from sweetheart import BaseConfig,echo,logging

# ensure Sweetheart runs in a development purpose
if os.getenv("SWS_OPERATING_STATE") != "development":
    logging.error("Module sweetheart.transitional must be operated in development state.")
    sys.exit(1)


class bin:
    # provide paths to local commands
    mdbook = f"{os.HOME}/.cargo/bin/mdbook"
    python = f"{os.getenv('SWS_PYTHON_ENV')}/bin/python3"
    geldata = f"{os.getenv('SWS_PYTHON_ENV')}/bin/gel"
    ipykernel = f"{python} -m ipykernel"


class ProjectInstaller:

    @classmethod
    def installer(cls,include=None,exclude=None):

        if include:
            listed = [i.strip() for i in include.split("|")]

        elif exclude:
            parts = "sys|rust|python|node|conf|doc|data"
            listed = [i for i in parts.split("|") if i not in exclude]

        # determine which parts to install
        enable = lambda part:  part in listed

        if enable("sys") and cls.libs.get("apt"):
            os.run(["sudo","apt-get","install",*cls.libs["apt"]])

        # if sys_ok and cls.libs.get("snap"):
        #     #FIXME: install snap packages
        #     os.run(["sudo","snap","install",*cls.libs["snap"]])

        # if rust_ok and "librust" in cls.libs:
        #     #FIXME: install crates from dist packages
        #     libs = [f"librust-{l}-dev" for l in cls.libs["librust"]]
        #     os.run(["sudo","apt-get","install",*libs])

        if enable("rust") and cls.libs.get("cargo"):

            if not os.which("cargo") and enable("sys"):
                os.run("sudo snap install rustup --classic")

            os.run(["cargo","install",*cls.libs["cargo"]])

        if enable("node") and \
        (cls.libs.get("npm") or cls.libs.get("npm-dev")):

            if not os.which("npm") and enable("sys"):
                os.run("sudo snap install node --classic")

            cwd = cls.path['node']
            os.makedirs(cwd,mode=0o755,exist_ok=True)
            os.run("npm init -y",cwd=cwd)

            if cls.libs.get("npm-dev"):
                os.run(["npm","install","-D",*cls.libs["npm-dev"]],cwd=cwd)

            if cls.libs.get("npm"): 
                os.run(["npm","install",*cls.libs["npm"]],cwd=cwd)

            # # provide a convenient link to jsx files
            # jsx= f"{cls.path.get('node')}/typescript"
            # if os.path.isdir(jsx) and cls.path.get("jsx"):
            #     os.symlink(jsx,cls.path["jsx"],target_is_directory=True)

        if enable("python") and cls.libs.get("pip"):
            #NOTE: poetry is used here instead of pip

            if not os.which("poetry") and enable("sys"):
                os.run("sudo apt-get install python3-poetry")

            cwd = cls.path["python"] 
            os.makedirs(cwd,mode=0o755,exist_ok=True)

            assert getattr(cls,"project",None),\
                "Project name must be set as class attribute before installing python dependencies."

            os.run(f"poetry init -C {cwd} -n --no-ansi --name={cls.project}")
            os.run(["poetry","-C",cwd,"--no-ansi","add",*cls.libs["pip"]])

        if enable("doc") and cls.path.get("doc"):
            # provide an empty mdbook directory for documentation
            os.makedirs(cls.path["doc"],mode=0o755,exist_ok=True)
            os.run(f"{bin.mdbook} init --force",cwd=cls.path["doc"])

        if enable("conf") and cls.path.get("conf"):
            #FIXME: provide default configuration files
            os.makedirs(cls.path["conf"],mode=0o755,exist_ok=True)
            # os.copy(f"{cls.source['conf']}/unit.json",cls.path["conf"])

        if enable("data") and cls.path.get("edgedb"):

            if not os.which(bin.geldata) and enable("python"):
                os.run(["poetry","-C",cls.path["python"],"--no-ansi","add","gel"])

            # provide an empty gel data project directory
            os.makedirs(cls.path["edgedb"],mode=0o755,exist_ok=True)
            os.run([bin.geldata,"init"],cwd=cls.path["edgedb"])


class SweetheartMaster(ProjectInstaller):

    libs = { #FIXME
        "apt": 
            ["unit",f"unit-python3.{python_version_tuple()[1]}"],
        "pip": # poetry
            ["gel","pydantic","ipykernel"],
        "npm-dev": 
            ["typescript","tailwindcss","solid-js","parcel"],
        "npm":
            ["@observablehq/plot"]
    }

    source = {
        # Sweetheart github repository source paths
        # this asssumes repo has been cloned in the /home dir
        "conf": f"{os.HOME}/Sweetheart/configuration",
        "doc": f"{os.HOME}/Sweetheart/documentation",
        "node": f"{os.HOME}/Sweetheart/code.node/solid",
        "python": f"{os.HOME}/Sweetheart/code.python",
    }

    path = {
        # set running directories
        "dist-dir": f"{os.HOME}/{BaseConfig.basedir}/application",# html
        "mdbk-dir": f"{os.HOME}/{BaseConfig.basedir}/documentation",# html

        # provide user working directories
        "conf": f"{os.HOME}/My_code/configuration",
        "doc": f"{os.HOME}/My_code/documentation",
        "node": f"{os.HOME}/My_code/webapp",
        "python": f"{os.HOME}/My_code/python",
        "edgedb": f"{os.HOME}/My_code/database",
    }

    scripts = {
        "mdbook-build": f"{bin.mdbook} build --dest-dir {path['mdbk-dir']} {source['doc']}",
        "node-build": f"npx parcel build --cache-dir {path['dist-dir']}/.parcel-cache --dist-dir {path['dist-dir']}",
    }

    @classmethod
    def initdev(cls):
        """ Install required packages and setup master project. """

        echo(f"Development Environment Setup")
        # cls.project = BaseConfig.master_project
        cls.installer(exclude="sys|node|python")
        os.copy(f"{cls.source['conf']}/unit.json",cls.path["conf"])

        # build sweetheart documentation from source
        echo("Build Provided Documentation",prefix="\n")
        os.run(cls.scripts["mdbook-build"],cwd=cls.source["doc"])

        # install python env dependencies from source
        echo("Install Python Dependencies",prefix="\n")
        os.run("poetry -n --no-root --no-ansi install",cwd=cls.source["python"])

        # provide directory for user python code
        os.makedirs(cls.path["python"],mode=0o755,exist_ok=True)

        # build sweetheart user interface from source
        echo("Build User Interface",prefix="\n")
        os.makedirs(cls.path["dist-dir"],mode=0o755,exist_ok=True)
        os.run("npm install",cwd=cls.source["node"])
        os.run(cls.scripts["node-build"],cwd=cls.source["node"])


class SweetheartProject(ProjectInstaller):

    libs = {
        "pip": 
            [ "ipykernel" ],
        "npm-dev": 
            [ "typescript", "tailwindcss", "parcel" ],
    }

    @classmethod
    def initdev(cls,project:str,homedir:str|None=None):
        """ Initialize a new project with the default structure. """

        cls.project = project # used within poetry init
        homedir = homedir or f"{os.HOME}/{project.capitalize()}"
        config = BaseConfig(project=project,homedir=homedir)

        cls.path = {
            # # set running directories
            # "dist-dir": f"{homedir}/application",# html
            # "mdbk-dir": f"{homedir}/documentation",# html

            # set user working directories
            "conf": f"{homedir}/configuration",
            "doc": f"{homedir}/documentation",
            "node": f"{homedir}/webapp",
            "python": f"{homedir}/python",
            # "edgedb": f"{homedir}/database",
        }

        echo(f"Initializing New Project")
        cls.installer(include="python|node|conf|doc")

        with open(config.conffile,"w") as file_out:
            json.dump(config.data,file_out,indent=4)
            logging.info(f"New config.json file created: {config.conffile}.")


class JupyterLab(ProjectInstaller):

    libs = { 
        "pip": 
            [ "jupyterlab" ] 
    }

    @classmethod
    def initdev(cls,project:str,homedir:str|None=None):
        """ Install JupyterLab and set it up to work with Sweetheart. """

        cls.project = project
        homedir = homedir or f"{os.HOME}/{project.capitalize()}"
        cls.path = { "python": f"{homedir}/python" }

        echo(f"JupyterLab Setup")
        cls.installer(include="python")