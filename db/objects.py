# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, Integer


class BaseDbObject:
    """Base class for every Miyagi model.
    Provides an aoutoincrement pk and few useful api.
    """
    uid = Column(BigInteger().with_variant(Integer, 'sqllite'),
                 primary_key=True,
                 autoincrement=True)

    def items(self, with_key=False):
        """Emulates dict's items() on the SQLAlchemy model."""
        for col in self.__class__.__table__.columns:
            if col.key != 'uid' or with_key:
                yield col.key, self.__dict__.get(col.key, None)
