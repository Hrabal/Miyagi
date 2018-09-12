# -*- coding: utf-8 -*-
import pendulum
from elasticsearch import Elasticsearch

from .constants import CRUD


class ElasticManager:
    """Manager class fro the Elasticsearch use."""
    es = None  # We always need one of those

    def __init__(self, app):
        self.app = app
        self.es = Elasticsearch([self.app.config.ES.asdict(), ])

    @classmethod
    def update_es(cls, crud_action):
        # Wraps Db methods to concurrently update ElasticSearch if avaiable
        # TODO: Make it ASYNC
        def es_manager(fnc):
            def wrapped(inst, *args, **kargs):
                try:
                    fnc(*args, **kargs)
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
                    getattr(cls.es, method)(**es_kwargs)
            # If no elasticsearch configuration is given, the normal function is returned
            return wrapped if cls.es else fnc
        return es_manager
