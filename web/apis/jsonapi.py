from vibora.responses import JsonResponse

from .miyagi_types import TypedMany
from .web import MiyagiRoute
from .miyagi import App


class JsonApiHandlers:
    def __init__(self, obj, app):
        self.obj = obj

    def make(self):
        for handler_factory in (self.base_collection, ):
            yield from handler_factory()

    def base_collection(self):
        uri = '/'.join(part.name.lower() for part in self.obj.path)

        async def base_collection(app: App):
            return JsonResponse({
                "links": {
                    "self": f"{self.webapp.url_scheme}://{app.config.host}/jsonapi/{uri}"
                },
                "data": [{
                    "type": self.obj.name,
                    "id": resource.uid,
                    "attributes": {
                        k: v for k, v in resource.items() if not isinstance(v, TypedMany)
                    }
                } for resource in app.db.query(self.obj.cls).all()]
            })
        base_collection.__name__ = f'{self.obj.name.lower()}_collection'
        yield MiyagiRoute(f'/{uri}', ['GET'], base_collection)
