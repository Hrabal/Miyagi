# -*- coding: utf-8 -*-
import inspect
from sqlalchemy import Column, BigInteger, Integer, DateTime

from ..web.session_manager import current_user
from ..tools import utc_now


class BaseDbObject:
    """Base class for every Miyagi model.
    Provides an autoincrement pk and few useful api.
    """
    uid = Column(Integer, primary_key=True, autoincrement=True)
    creation_datetime = Column(DateTime, default=utc_now)
    creation_user = Column(BigInteger, default=current_user)
    update_datetime = Column(DateTime, onupdate=utc_now, default=utc_now)
    update_user = Column(BigInteger, onupdate=current_user, default=current_user)

    def items(self, system_attributes=True):
        """Emulates dict's items() on the SQLAlchemy model."""
        for col in self.__class__.__table__.columns:
            if not system_attributes and col.key in BaseDbObject._system_cols():
                # We skip the system attributes if asked to do so
                continue
            else:
                yield col.key, self.__dict__.get(col.key, None)

    @classmethod
    def _system_cols(cls):
        return set(k for k, o in inspect.getmembers(cls)
                   if not inspect.isfunction(o) and not k.startswith('__'))

    def __repr__(self):
        return f'<{self.__class__.__name__} uid: {self.uid}>'

    @classmethod
    def new(cls, **kwargs):
        return cls(**kwargs)

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
            if k in BaseDbObject._system_cols():
                setattr(self, k, v)
