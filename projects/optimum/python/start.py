
from flow import ProcessUnit
from sweetheart.services import *

# Set App Configuration:

config = set_config({
    # set here your own app config when required
    # but please refer to the documentation first
})

# Set Python Asgi/3 App for data:

# create here a runable entry point for your data traffic
# default and recommended is a PostgresUnchained data driver at the url /geldata
# NOTE: Sweetheart aims to serve statics directly via NginxUnit, not Asgi/3

webapp = WebappServer(config).app(
    DataHub("/flowdata",ProcessUnit()) )
