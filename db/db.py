# -*- coding: utf-8 -*-
from sqlalchemy import Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import types as SQLtypes

from .objects import BaseDbObject
from .constants import TYP_MAP

from ..exceptions import MiyagiDbError
from ..tools import objdict, MiyagiEnum

SQLAlchemyBase = declarative_base()


def transcode_type(typ):
    """Transcode a Python/module type into a SQLAlchemy type
    If no mapping is found, the given type is used so we can define a
    Miyagi object's attribute directly using SQLAlchemy types
    """
    if issubclass(typ, MiyagiEnum):
        # Custom defined enumes
        return SQLtypes.Enum(typ)
    if issubclass(typ, BaseDbObject):
        # Objects classes transposed to object ids
        return SQLtypes.Integer
    for p_type, sql_type in TYP_MAP:
        if issubclass(typ, p_type):
            return sql_type
    # Fallback
    return SQLtypes.Unicode


class Db:
    models = objdict()

    def __init__(self, app):
        self.app = app
        self.config = app.config
        try:
            # Check if we have valid db config
            self.config.DB.type is True
        except AttributeError:
            raise MiyagiDbError('No DB config found.'
                                'Please provide the needed parameters inside the "DB" key in the config file.')

        self.SQLAlchemyBase = SQLAlchemyBase
        self.db_engine = create_engine(self.config.db_uri, echo=True)
        self.session_maker = sessionmaker(autoflush=False)
        self.session_maker.configure(bind=self.db_engine)

    def digest_objects(self, objects):
        for obj in objects:
            # Make a SQLAlchemy model out of this class
            # and register the model in the Db instance
            # and in the BaseDbObject instance
            self.models[obj.name] = obj.cls = self.craft_sqalchemy_model(obj)

    def session(self):
        return self.session_maker()

    @property
    def metadata(self):
        return self.SQLAlchemyBase.metadata

    def craft_sqalchemy_model(self, obj):
        return type(
            obj.name,
            (BaseDbObject, self.SQLAlchemyBase, ),
            {
                **{
                    '__tablename__': '_'.join(part.name.lower() for part in obj.path),
                    '_db': self,  # For db-accessing apis on the Objects
                    '_app': self.app,  # For app/app components access
                    '_indexed': BaseDbObject._indexed + getattr(obj._original_cls, '_indexed', tuple()),
                },
                **{k: Column(transcode_type(typ))
                   for k, typ in obj._original_cls.__annotations__.items()
                   if k not in BaseDbObject._system_cols()  # those are inherited
                   }
            }
        )
