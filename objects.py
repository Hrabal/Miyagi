# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer


class Thing:
    uid = Column(Integer, primary_key=True, autoincrement=False)

    def items(self):
        for col in self.__class__.__table__.columns:
            if col.key != 'uid':
                yield col.key, self.__dict__.get(col.key, None)


class TypedMany:
    pass


class Type:
    pass
