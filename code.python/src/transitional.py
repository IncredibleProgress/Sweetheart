from sweetheart import BaseConfig
from sweetheart.subprocess import os
from platform import python_version_tuple

# ensure Sweetheart runs in a development purpose
assert os.getenv("SWS_OPERATING_STATE") == "development"

class bin:
    # provide paths to local binaries
    mdbook = f"{os.HOME}/.cargo/bin/mdbook"


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
            os.makedirs(cwd,exist_ok=True)
            os.run("npm init -y",cwd=cwd)

            if cls.libs.get("npm-dev"):
                os.run(["npm","install","-D",*cls.libs["npm-dev"]],cwd=cwd)

            if cls.libs.get("npm"): 
                os.run(["npm","install",*cls.libs["npm"]],cwd=cwd)

            # provide a convenient link to jsx files
            jsx= f"{cls.path.get('node')}/typescript"
            if os.path.isdir(jsx) and cls.path.get("jsx"):
                os.symlink(jsx,cls.path["jsx"],target_is_directory=True)

        if enable("python") and cls.libs.get("pip"):
            #NOTE: poetry is used here instead of pip

            if not os.which("poetry") and enable("sys"):
                os.run("sudo apt-get install python3-poetry")

            cwd = cls.path.get("python") 
            os.makedirs(cwd,exist_ok=True)

            os.run(f"poetry init -C {cwd} -n --no-ansi --name={BaseConfig.master_project}")
            os.run(["poetry","-C",cwd,"--no-ansi","add",*cls.libs["pip"]])

        if enable("doc") and cls.path.get("doc"):
            # provide an empty mdbook directory for documentation
            os.makedirs(cls.path["doc"],exist_ok=True)
            os.run(f"{bin.mdbook} init --force",cwd=cls.path["doc"])

        if enable("conf") and cls.path.get("conf"):
            os.makedirs(cls.path["conf"],exist_ok=True)

        if enable("data") and cls.path.get("data"):
            # provide an empty gel data project directory
            os.makedirs(cls.path["data"],exist_ok=True)
            os.run("gel init",cwd=cls.path["data"])


class ProjectSweetheart(ProjectInstaller):

    libs = {
        "apt": 
            ["unit",f"unit-python3.{python_version_tuple()[1]}"],
        "pip": # poetry
            ["gel","pydantic","ipykernel"],
        "npm-dev": #FIXME
            ["typescript","tailwindcss","solid-js","parcel"],
        "npm":
            ["@observablehq/plot"]
    }

    source = {
        # Sweetheart github repository source paths
        # this asssumes repo has been cloned in the home dir
        "doc": f"{os.HOME}/Sweetheart/documentation",
        "node": f"{os.HOME}/Sweetheart/code.node/solid",
        "conf": f"{os.HOME}/Sweetheart/configuration",
        "python": f"{os.HOME}/Sweetheart/code.python",
    }

    path = {
        # set running directories
        "node": f"{os.HOME}/{BaseConfig.basedir}/user_interface",# jsx
        "dist-dir": f"{os.HOME}/{BaseConfig.basedir}/application",# html
        "doc-dev": f"{os.HOME}/{BaseConfig.basedir}/documentation",# html

        # provide user working directories
        "conf": f"{os.HOME}/My_code/configuration",
        "doc": f"{os.HOME}/My_code/documentation",
        "jsx": f"{os.HOME}/My_code/typescript",#! link
        "python": f"{os.HOME}/My_code/python",
        "data": f"{os.HOME}/My_code/database",
    }

    scripts = {
        "mdbook-build": f"{bin.mdbook} build --dest-dir {path['doc-dev']} {source['doc']}",
        "node-build": f"npx parcel build --cache-dir {path['dist-dir']}/.parcel-cache --dist-dir {path['dist-dir']}",
    }

    @classmethod
    def initdev(cls):
        """ install required packages and setup project structure """

        cls.installer(exclude="node|python")

        # build sweetheart documentation from source
        os.run(cls.scripts["mdbook-build"],cwd=cls.source["doc"])

        # install python dependencies into venv from source
        os.run(["poetry","-n","--no-root","--no-ansi","install",
            *cls.libs["pip"]],cwd=cls.source["python"])

        # provide directory for user python code
        os.makedirs(cls.path["python"],exist_ok=True)

        # build the sweetheartuser interface from source
        os.makedirs(cls.path["dist-dir"],exist_ok=True)
        os.run("npm install",cwd=cls.source["node"])
        os.run(cls.scripts["node-build"],cwd=cls.source["node"])
