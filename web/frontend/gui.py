from vibora.responses import Response

from ...miyagi import App
from ..web import MiyagiRoute
from .templates.base import MiyagiBase


class Gui:
    def __init__(self, app: App):
        self.app = app

    def craft(self):
        yield from self.home()

    def home(self):
        async def home_handler(app: App):
            output = MiyagiBase(app).render()
            return Response(output.encode())

        yield MiyagiRoute(f'/app', ['GET', ], home_handler)
