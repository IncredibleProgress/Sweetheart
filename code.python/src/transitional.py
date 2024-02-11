
from sweetheart.subprocess import os

def init():

    HOME = os.expanduser("~")

    node = os.stdout("which node")
    cargo = os.stdout("which cargo")
    poetry = f"{HOME}/.local/bin/poetry"

    # unit = os.stdout("which unitd")
    # rethinkdb = os.stdout("which rethinkdb")

    install = []
    if not node: install.append("nodejs")
    if not cargo: install.append("cargo")
    if install: os.run(["sudo","apt","install",*install])

    if not os.isfile(poetry):
        os.run("curl -sSL https://install.python-poetry.org | python3 -")

    os.makedirs(f"{HOME}/.sweet/application/typescript/")
    os.mkdir(f"{HOME}/.sweet/configuration/")
    os.mkdir(f"{HOME}/.sweet/documentation/")
    
    os.makedirs(f"{HOME}/.sweet/my_code/python")
    os.symlink(f"{HOME}/.sweet/application/typescript/",f"{HOME}/.sweet/my_code/react")
    