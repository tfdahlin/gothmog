from functools import wraps
import os, logging

import config

from pycnic.core import Handler
from pycnic.errors import HTTP_400, HTTP_403
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO, filename=config.log_file)

db_uri = f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite")}'
engine = create_engine(db_uri)

class BaseHandler(Handler):
    """Provides a handful of useful methods to request handler classes."""
    def before(self):
        self.base_request = f'[{self.request.ip}] -- {self.request.method}'
        self.response.set_header('Access-Control-Allow-Origin', '*')

    def HTTP_200(self, data={}):
        if 'version' not in data:
            data['version'] = config.API_VERSION

        self.response.status_code = 200
        result = {
            'status': '200 OK',
            'status_code': '200',
            'data': data,
            'error': None
        }

        return result

    def HTTP_400(self, data={}, error='Bad Request'):
        if 'version' not in data:
            data['version'] = config.API_VERSION

        self.response.status_code = 400
        result = {
            'status': '400 Bad Request',
            'status_code': '400',
            'data': data,
            'error': error,
        }
        return result
    
    def HTTP_404(self, data={}, error='Not Found'):
        if 'version' not in data:
            data['version'] = config.API_VERSION

        self.response.status_code = 404
        result = {
            'status': '404 Not Found',
            'status_code': '404',
            'data': data,
            'error': error,
        }
        return result

def requires_params(*params):
    """Determine if all necessary parameters are present, return 400 if not.
    Arguments:
        params (list or strings): Required parameters for the request.
    Raises:
        HTTP_400: Raised if at least one parameter is missing.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not params:
                logger.warn("require_params decorator used without any parameters specified.")
                return f(*args, **kwargs)

            missing_params = []

            # Iterate through required params to find if any are missing.
            for param in params:
                # Append all missing params to the list of missing params.
                if param not in args[0].request.data:
                    missing_params.append(param)

            # If there were any missing parameters, return a descriptive error.
            if len(missing_params) > 0:
                logger.info('require_params decorator found missing parameters in request.')
                raise HTTP_400(f"Error, missing parameters: {', '.join(missing_params)}")
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def verify_peer():
    """Determine if the remote peer is in the allowed list in the config or not.
    
    Raises:
        HTTP_403: Raised if the remote peer is missing.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            remote_ip = args[0].request.environ['REMOTE_ADDR']
            #remote_ip = args[0].request.environ['gunicorn.socket'].getpeername()

            #if remote_ip[0] not in config.allowed_hosts:
            logger.info(f'Remote ip: {remote_ip}')
            if remote_ip not in config.allowed_hosts:
                raise HTTP_403('Forbidden.')
            return f(*args, **kwargs)
        return wrapped
    return wrapper
