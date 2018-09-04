# -*- coding: utf-8 -*-
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, create_engine

from ..objects import MiyagiObject
from ..tools import objdict

SQLAlchemyBase = declarative_base()


class Db:
    models = objdict()

    def __init__(self, app):
        self.app = app
        try:
            self.app.config.DB is True
        except AttributeError:
            print('WARNING!! No DB config found.')
        else:
            self.SQLAlchemyBase = SQLAlchemyBase
            self.db_engine = create_engine(self.app.config.db_uri, echo=True)
            self.session_maker = sessionmaker(autoflush=False)
            self.session_maker.configure(bind=self.db_engine)

        for obj in self.app.objects:
            # Make a SQLAlchemy model out of this class
            obj.cls = self.craft_sqalchemy_model(obj)

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
