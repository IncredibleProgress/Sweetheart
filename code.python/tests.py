
from sys import argv
from sweetheart.services import *


def test_set_unit_config():

    config = set_config({})

    webapp = WebappServer(config).mount(
        'Route("/",HTMLResponse("<h1>Starlette is OK!</h1>"))' )

    webapp.set_service(put_config=True)


if __name__ == "__main__":

    if argv[1]=="unit-conf": test_set_unit_config()