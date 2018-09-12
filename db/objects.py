# -*- coding: utf-8 -*-
import inspect
from sqlalchemy import Column
from sqlalchemy import types as SQLtypes

import pendulum
from pendulum import DateTime, Date, Time, Period
from datetime import datetime
from decimal import Decimal

from ..web.session_manager import current_user
from ..tools import utc_now

PYT_TYPES = (int, bool, Date, DateTime, float, Decimal, Period, str, Time)
ORM_TYPES = (SQLtypes.BigInteger, SQLtypes.Boolean, SQLtypes.Date, SQLtypes.DateTime, SQLtypes.Float, SQLtypes.Numeric, SQLtypes.Interval, SQLtypes.Unicode, SQLtypes.Time)
TYP_MAP = zip(PYT_TYPES, ORM_TYPES)


class BaseDbObject:
    """Base class for every Miyagi model.
    Provides an autoincrement pk and few useful api.
    """
    uid = Column(SQLtypes.Integer,
                 primary_key=True,
                 autoincrement=True)
    creation_datetime = Column(SQLtypes.DateTime,
                               default=utc_now)
    creation_user = Column(SQLtypes.BigInteger,
                           default=current_user)
    update_datetime = Column(SQLtypes.DateTime,
                             onupdate=utc_now,
                             default=utc_now)
    update_user = Column(SQLtypes.BigInteger,
                         onupdate=current_user,
                         default=current_user)

    def items(self, sys_attrs=True):
        """Emulates dict's items() on the SQLAlchemy model."""
        for col in self.__class__.__table__.columns:
            if not sys_attrs and col.key in BaseDbObject._system_cols():
                # We skip the system attributes if asked to do so
                continue
            else:
                val = self.__dict__.get(col.key, None)
                if isinstance(val, datetime):
                    yield col.key, pendulum.instance(val)
                else:
                    yield col.key, val

    @classmethod
    def _system_cols(cls):
        return set(k for k, o in inspect.getmembers(cls)
                   if not inspect.isfunction(o) and not k.startswith('__'))

    def __repr__(self):
        return f'<{self.__class__.__name__} uid: {self.uid}>'

    @classmethod
    def query(cls, *org, **kwargs):
        return cls._db.session().query(cls)

    @classmethod
    def new(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def count(cls):
        return cls._db.session().query(cls).count()

    def save(self):
        s = self._db.session()
        s.add(self)
        s.commit()

    def delete(self):
        s = self._db.session()
        s.delete(self)
        s.commit()

    def set_dict(self, data_dict: dict):
        for k, v in data_dict:
            if k not in BaseDbObject._system_cols():
                setattr(self, k, v)
