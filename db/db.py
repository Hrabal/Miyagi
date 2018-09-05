# -*- coding: utf-8 -*-
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, create_engine

from ..exceptions import MiyagiDbError
from ..objects import MiyagiObject
from ..tools import objdict, MiyagiEnum

SQLAlchemyBase = declarative_base()


class DbTypes(MiyagiEnum):
    SQLLITE = 'sqlite'
    AWS = 'AWS'


class DBEngines(MiyagiEnum):
    POSTGRES = 'postgres'
    MYSQL = 'mysql'


class Db:
    models = objdict()

    def __init__(self, app):
        self.app = app
        try:
            # Check if we have valid db config
            self.app.config.DB is True
        except AttributeError:
            raise MiyagiDbError('No DB config found. Please provide the needed parameters inside the "DB" key in the config file.')
        else:
            self.SQLAlchemyBase = SQLAlchemyBase
            self.db_engine = create_engine(self.db_uri, echo=True)
            self.session_maker = sessionmaker(autoflush=False)
            self.session_maker.configure(bind=self.db_engine)
            for obj in self.app.objects:
                # Make a SQLAlchemy model out of this class
                obj.cls = self.craft_sqalchemy_model(obj)

    @property
    def db_uri(self):
        """Generates a db connection uri or name based on the dbtype"""
        if self.app.config.DB.type == DbTypes.AWS.value:
            return f'{self.app.config.DB.engine}://{self.app.config.DB.user}:{self.app.config.DB.pwd}@{self.app.config.DB.uri}/{self.DB.dbname}'
        elif self.app.config.DB.type == DbTypes.SQLLITE.value:
            return f'{self.app.config.DB.type}:///{self.app.config.project_name.lower()}.db'
        else:
            raise MiyagiDbError('No db configuration found')

    @property
    def db_repo(self):
        return f'{self.app.config.project_name.lower()}_db_repo'

    def session(self):
        return self.session_maker()

    @property
    def metadata(self):
        return self.SQLAlchemyBase.metadata

    def craft_sqalchemy_model(self, obj):
        model = type(
            obj.name,
            (MiyagiObject, SQLAlchemyBase),
            {
                **{'__tablename__': '_'.join(part.name.lower() for part in obj.path)},
                **{'_db': self},
                # TODO Type mapping below
                **{k: Column(Unicode()) for k, typ in obj._original_cls.__annotations__.items() if k != 'uid'},
            }
        )
        self.models[obj.name] = model
        return model
