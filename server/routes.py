import logging, uuid, datetime, re, os, secrets
from wsgiref.util import FileWrapper

from util import BaseHandler, engine, requires_params, verify_peer
import models

from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
