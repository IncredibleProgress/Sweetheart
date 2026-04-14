from sys import argv
from sweetheart.services import *


def test_initCaddyService():

    config = set_config()

    # provide some useful info
    echo("Caddyfile path:",config.caddyfile)
    echo("python app directory:",config['python_app']['path'])

    # set Caddy web server
    WebappServer(config).set_service(systemctl=True)


if __name__ == "__main__":
    pass