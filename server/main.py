#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: server/main.py

# Native python imports

# PIP library imports
from pycnic.core import WSGI, Handler

# Local file imports
import apps.commands.routes as commands_routes
import apps.files.routes as files_routes
import apps.ops.routes as ops_routes
from models import Base
import routes
from util import BaseHandler, engine

class app(WSGI):
    """WSGI wrapper class for pycnic routing."""
    routes = [
        # General routes
        *routes.routes,

        # Routes for managing ops.
        *ops_routes.routes,

        # Routes for managing files.
        *files_routes.routes,

        # Client resources
        *commands_routes.routes,
    ]

# Some WSGI server expects to find something called application, rather than app,
#  but I can't remember which it was.
application = app

if __name__ == "__main__":
    # Database setup if main is run on its own.
    Base.metadata.create_all(engine)
