# -*- coding: utf-8 -*-
from .db.objects import BaseDbObject


class MiyagiObject(BaseDbObject):

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


class TypedMany:
    pass


class Type:
    pass
