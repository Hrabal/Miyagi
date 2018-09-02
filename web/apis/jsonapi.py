# -*- coding: utf-8 -*-
from vibora.responses import JsonResponse

from ...objects import TypedMany
from ..web import MiyagiRoute, MiyagiBlueprint
from ...miyagi import App


class JsonApi(MiyagiBlueprint):
    base_path = '/jsonapi'

    @property
    def endpoints(self):
        for _, process in self.app.processes.items():
            for obj in process.objects:
                if obj._json_api:
                    for handler_factory in (self.base_collection, ):
                        yield from handler_factory(obj)

    def base_collection(self, obj):
        uri = f'{self.base_path}/{"/".join(part.name.lower() for part in obj.path)}'

        async def base_collection_blueprint(app: App):
            return JsonResponse({
                "links": {
                    "self": f"{self.app.webapp.url_scheme}://{self.app.config.host}/{uri}"
                },
                "data": [{
                    "type": obj.name,
                    "id": resource.uid,
                    "attributes": {
                        k: v for k, v in resource.items() if not isinstance(v, TypedMany)
                    }
                } for resource in app.db.query(obj.cls).all()]
            })
        base_collection_blueprint.__name__ = f'{obj.name.lower()}_collection'
        yield MiyagiRoute(f'{uri}', ['GET', ], base_collection_blueprint)
