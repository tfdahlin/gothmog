#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: server/routes.py

# Native python imports
import datetime, logging, os, re, secrets, uuid
from wsgiref.util import FileWrapper

# PIP library imports
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

# Local file imports
from util import BaseHandler, engine, requires_params, verify_peer
import models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

Session = sessionmaker(bind=engine)

class access_db:
    """Wrapper class for accessing the database.

    This automatically closes database connectiosn on completion,
    and is designed solely for convenience.

    Example:
    with access_db() as conn:
        my_obj = do_stuff()
        db_conn.add(my_obj)
        db_conn.commit()
    """

    def __enter__(self):
        """Connects to the database and returns the connection as part of the setup process."""
        self.db_conn = Session()
        return self.db_conn

    def __exit__(self, type, value, traceback):
        """Closes the db connection as part of the teardown process."""
        self.db_conn.close()

class Ping(BaseHandler):
    """Ping/pong URI."""
    def get(self):
        return self.HTTP_200(data={'msg': 'Pong!'})

class Home(BaseHandler):
    """Not sure what I want to do with this just yet. Currently always returns 200 code."""
    def get(self):
        return self.HTTP_200()

routes = [
    ('/', Home()),
    ('/ping', Ping()),
]
