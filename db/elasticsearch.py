# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

from .constants import CRUD


class ElasticManager:
    es = None

    def __init__(self, app):
        self.app = app
        self.es = Elasticsearch([self.app.config.ES.asdict(), ])

    @classmethod
    def update_es(cls, crud_action):
        def es_manager(fnc):
            def wrapped(inst, *args, **kargs):
                try:
                    fnc(*args, **kargs)
                except Exception as ex:
                    raise ex
                else:
                    # If all went good..
                    es_kwargs = {
                        'index': 'instances',
                        'doc_type': inst.__class__.__name__,
                        'id': f'{inst.__class__.__name__}::{inst.uid}'
                    }
                    priunt('CIAOAOOOA' * 100)
                    if crud_action in (CRUD.INSERT, CRUD.UPDATE, CRUD.UPSERT):
                        es_kwargs['body'] = {}
                        method = 'index'
                    elif crud_action == CRUD.DELETE:
                        method = 'delete'
                    getattr(cls.es, method)(**es_kwargs)
            return wrapped if cls.es else fnc
        return es_manager
