# -*- coding: utf-8 -*-
import inspect
import pendulum
from elasticsearch import Elasticsearch

from .constants import CRUD


class ElasticManager:
    """Manager class fro the Elasticsearch use."""

    def __init__(self, app):
        self.app = app
        self.es = Elasticsearch([self.app.config.ES.asdict(), ])
        self.bind_db(app.db)

    @classmethod
    def mark_es(cls, crud_action):
        def es_manager(fnc):
            fnc._es_crud_action = crud_action
            return fnc
        return es_manager

    def bind_db(self, db):
        def wrap(method, wrapped, crud_action):
            def wrapped(inst, *args, **kargs):
                try:
                    res = method(inst, *args, **kargs)
                except Exception as ex:
                    # All exceptions are encouraged
                    raise ex
                else:
                    # If all went good..
                    es_kwargs = {
                        'index': 'instances',
                        'doc_type': inst.__class__.__name__,
                        'id': f'{inst.__class__.__name__}::{inst.uid}'
                    }
                    # Switch the ElastichSearch method and enrich the kwargs accordingly
                    if crud_action in (CRUD.INSERT, CRUD.UPDATE, CRUD.UPSERT):
                        es_kwargs['body'] = {
                            'timestamp': pendulum.now(),
                            'text': inst.searchable_values
                        }
                        method = 'index'
                    elif crud_action == CRUD.DELETE:
                        method = 'delete'
                    es_res = getattr(self.es, method)(**es_kwargs)
                    return res
            return wrapped
        for _, model in db.models.items():
            for m_name, method in inspect.getmembers(model, inspect.ismethod):
                try:
                    setattr(model, m_name, wrap(method, method._es_crud_action))
                except AttributeError:
                    pass
