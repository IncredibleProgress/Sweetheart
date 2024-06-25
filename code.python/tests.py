
from sys import argv
from sweetheart.services import *
from sweetheart.subprocess import os
from sweetheart.transitional import init_project


def test_install_all():

    echo("remove any existing env ...",prefix="\n")
    os.run(["rm","-R","~/.sweet"])

    echo("setting up master env of sweetheart ...",prefix="\n")
    init_project("sweetheart",dict(
        apt = ["unit","rethinkdb"],
        pip = ["rethinkdb","ipykernel"],
        npm = ["react","react-dom","@types/react","@types/react-dom","tailwindcss"] ))

    echo("setting up new env for jupyterlab ...",prefix="\n")
    init_project("jupyter",{"pip":["jupyterlab"]})

    echo("setting up new env for sandbox ...",prefix="\n")
    init_project("sandbox",{})


def test_set_unit_config():

    config = set_config({})

    webapp = WebappServer(config).mount(
        'Route("/",HTMLResponse("<h1>Asgi Server is OK!</h1>"))' )

    webapp.set_service(put_config=True)


if __name__ == "__main__":

    if argv[1]=="unit-conf": test_set_unit_config()
    elif argv[1]=="install": test_install_all()
    else: print("Unknown test command")