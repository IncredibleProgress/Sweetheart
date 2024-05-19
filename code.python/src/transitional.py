
from sweetheart.subprocess import os


def init_project(project:str,libs=dict):

    HOME = os.expanduser("~")
    node = os.stdout("which node")
    cargo = os.stdout("which cargo")

    install = libs.get("apt",[])
    if not node: install.append("nodejs")
    if not cargo: install.append("cargo")
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
        cwd = f"{HOME}/.sweet/{project}/application"
        os.run("npm init -y",cwd=cwd)
        os.run(["npm","install",*libs["npm"]],cwd=cwd)

    if libs.get("pip"):
        cwd = f"{HOME}/.sweet/{project}/my_code/python"
        os.run(f"poetry init -C {cwd} -n --no-ansi --name={project}")
        os.run(["poetry","-C",cwd,"--no-ansi","add",*libs["pip"]])
