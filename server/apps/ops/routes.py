import logging, uuid, datetime, re, os, secrets
from urllib.parse import unquote
from wsgiref.util import FileWrapper

from util import BaseHandler, engine, requires_params, verify_peer
import models, config

from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO, filename=config.log_file)


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

class FetchAllCommands(BaseHandler):
    def get(self, op_name):
        logger.info(f'{self.base_request} /op/{op_name}/commands')
        op_name = unquote(op_name)
        all_commands = []
        try:
            data = {}
            with access_db() as db_conn:
                result = db_conn.query(models.Command).\
                    filter(models.Command.op_name==op_name).\
                    order_by(models.Command.created.desc())
                for cmd in result:
                    cmd_time = cmd.created.replace(microsecond=0)
                    transmissable_data = {
                        'guid': str(cmd.guid),
                        'op_name': cmd.op_name,
                        'type': cmd.cmd_type,
                        'cmd': cmd.cmd_data,
                        'created': str(cmd_time),
                    }
                    all_commands.append(transmissable_data)
        except Exception as e:
            logger.warn(e)
            return self.HTTP_400()
        else:
            data['commands'] = all_commands
            return self.HTTP_200(data=data)

class FetchOp(BaseHandler):
    """This should return the URL for the most recent command for a given op."""
    def get(self, op_name):
        logger.info(f'{self.base_request} /op/fetch/{op_name}')
        op_name = unquote(op_name)
        try:
            data = {}
            with access_db() as db_conn:
                latest = db_conn.query(models.Command).\
                    filter(models.Command.op_name==op_name).\
                    order_by(models.Command.created.desc()).\
                    limit(1).first()
        except Exception as e:
            logger.warn(e)
            return self.HTTP_400()
        else:
            if latest:
                data['guid'] = str(latest.guid)
                return self.HTTP_200(data=data)
            else:
                return self.HTTP_200()

class FetchAllOps(BaseHandler):
    def get(self):
        ops_list = []
        with access_db() as db_conn:
            all_ops = db_conn.query(models.OpName).all()
            for op in all_ops:
                ops_list.append(op.name)
        return self.HTTP_200(data={'ops': ops_list})

class CreateOp(BaseHandler):
    @verify_peer()
    @requires_params('op_name')
    def post(self):
        op_name = self.request.data['op_name']
        with access_db() as db_conn:
            exists = db_conn.query(models.OpName).\
                filter_by(name=op_name).scalar() is not None
            if not exists:
                try:
                    new_op = models.OpName(
                        guid = uuid.uuid4(),
                        name = op_name
                    )
                    db_conn.add(new_op)
                except Exception as e:
                    return self.HTTP_400()
                else:
                    db_conn.commit()
                    return self.HTTP_200()
            else:
                return self.HTTP_400()

class DeleteOp(BaseHandler):
    @verify_peer()
    @requires_params('op_name')
    def post(self):
        op_name = self.request.data['op_name']
        with access_db() as db_conn:
            existing_op = db_conn.query(models.OpName).\
                filter_by(name=op_name).first()
            existing_op_commands = db_conn.query(models.Command).\
                filter_by(op_name=op_name).all()
            if existing_op:
                try:
                    db_conn.delete(existing_op)
                    db_conn.commit()
                except Exception as e:
                    logger.warn(e)
            if existing_op_commands:
                for cmd in existing_op_commands:
                    try:
                        db_conn.delete(cmd)
                    except Exception as e:
                        logger.warn(e)
                db_conn.commit()
            return self.HTTP_200()

routes = [
    ('/op/create', CreateOp()),
    ('/op/delete', DeleteOp()),
    ('/op', FetchAllOps()),
    ('/op/fetch/([0-9a-zA-Z%_-]+)', FetchOp()),
    ('/op/([0-9a-zA-Z%_-]+)/commands', FetchAllCommands()),
]
