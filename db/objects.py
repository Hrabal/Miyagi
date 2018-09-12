# -*- coding: utf-8 -*-
import inspect
from sqlalchemy import Column, BigInteger, Integer, DateTime

from ..web.session_manager import current_user
from ..tools import utc_now


class BaseDbObject:
    """Base class for every Miyagi model.
    Provides an autoincrement pk and few useful api.
    """
    uid = Column(BigInteger().with_variant(Integer, 'sqllite'),
                 primary_key=True,
                 autoincrement=True)
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
