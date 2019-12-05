import uuid
import sqlalchemy
from sqlalchemy.types import TypeDecorator, CHAR, String
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Taken from: https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))


    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

class Command(Base):
    __tablename__ = 'c2_command'

    guid = Column(GUID, primary_key=True, nullable=False)
    op_name = Column(String, nullable=False)

    cmd_type = Column(String)
    cmd_data = Column(String)
    id = Column(Integer)
    created = Column(DateTime)
    next_cmd = Column(GUID)

class Upload(Base):
    __tablename__ = 'c2_file'
    
    guid = Column(GUID, primary_key=True, nullable=False)
    op_name = Column(String, nullable=False)

    filepath = Column(String)
    filename = Column(String, nullable=False)

class OpName(Base):
    __tablename__ = 'c2_op_name'
    
    guid = Column(GUID, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
   
