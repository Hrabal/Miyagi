from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, create_engine

from ..config import Config
from ..objects import Thing

SQLAlchemyBase = declarative_base()


class Db:
    def __init__(self, config: Config):
        self.config = config
        self.SQLAlchemyBase = SQLAlchemyBase
        self.db_engine = create_engine(self.config.db_uri)
        self.db_session = sessionmaker(autoflush=False)
        self.db_session.configure(bind=self.db_engine)
        self.query = self.db_session().query
        self.add = self.db_session().add

    @classmethod
    def craft_sqalchemy_model(cls, obj, table: str):
        return type(
            str(obj.__name__),
            (Thing, SQLAlchemyBase),
            {
                **{'__tablename__': table},
                # TODO Type mapping below
                **{k: Column(Unicode()) for k, typ in obj.__annotations__.items() if k != 'uid'}
            }
        )
