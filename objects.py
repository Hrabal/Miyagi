# -*- coding: utf-8 -*-
from .db.objects import BaseDbObject


class MiyagiObject(BaseDbObject):
    def __repr__(self):
        return f'<{self.__class__.__name__} uid: {self.uid}>'


class TypedMany:
    pass


class Type:
    pass
