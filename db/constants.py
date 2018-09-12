# -*- coding: utf-8 -*-
from decimal import Decimal
from pendulum import DateTime, Date, Time, Period
from sqlalchemy import types as SQLtypes


class CRUD:
    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    UPDATE = 'UPDATE'
    UPSERT = 'UPSERT'


PYT_TYPES = (int, bool, Date, DateTime, float, Decimal, Period, str, Time)
ORM_TYPES = (SQLtypes.BigInteger, SQLtypes.Boolean, SQLtypes.Date, SQLtypes.DateTime, SQLtypes.Float,
             SQLtypes.Numeric, SQLtypes.Interval, SQLtypes.Unicode, SQLtypes.Time)
TYP_MAP = zip(PYT_TYPES, ORM_TYPES)
