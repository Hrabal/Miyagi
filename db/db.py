# -*- coding: utf-8 -*-
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, create_engine

from ..config import Config
from ..objects import MiyagiObject
from ..tools import objdict

SQLAlchemyBase = declarative_base()


class Db:
    models = objdict()

    def __init__(self, config: Config):
        self.config = config
        try:
            self.config.DB is True
        except AttributeError:
            print('WARNING!! No DB config found.')
        else:
            self.SQLAlchemyBase = SQLAlchemyBase
            self.db_engine = create_engine(self.config.db_uri, echo=True)
            self.session_maker = sessionmaker(autoflush=False)
            self.session_maker.configure(bind=self.db_engine)

    def session(self):
        return self.session_maker()

    @property
    def metadata(self):
        return self.SQLAlchemyBase.metadata

    @classmethod
    def craft_sqalchemy_model(cls, obj, table: str):
        name = str(obj.__name__)
        model = type(
            name,
            (MiyagiObject, SQLAlchemyBase),
            {
                **{'__tablename__': table},
                # TODO Type mapping below
                **{k: Column(Unicode()) for k, typ in obj.__annotations__.items() if k != 'uid'}
            }
        )
        cls.models[name] = model
        return model
