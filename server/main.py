from pycnic.core import WSGI, Handler

from util import BaseHandler, engine

from models import Base

import routes
import apps.ops.routes as ops_routes
import apps.files.routes as files_routes
import apps.commands.routes as commands_routes

class app(WSGI):
    routes = [
        # General routes
        *routes.routes,

        # Routes for managing ops.
        *ops_routes.routes,

        # Routes for managing files.
        *files_routes.routes,

        # Client resources
        *commands_routes.routes,
        #('/cmd/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', apps.commands.Command()),
    ]

application = app

if __name__ == "__main__":
    Base.metadata.create_all(engine)
