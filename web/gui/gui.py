# -*- coding: utf-8 -*-
from vibora.responses import Response

from ...miyagi import App
from ..web import MiyagiRoute
from .templates.main_pages import MiyagiAppHome, ProcessesPage, ProcessPage


class Gui:
    def __init__(self, app: App):
        self.app = app

    @property
    def pages(self):
        yield self.page(MiyagiAppHome, '/app')
        yield self.page(ProcessesPage, '/app/processes')
        for p_name, process in self.app.processes.items():
            yield self.page(ProcessPage, f'/app/processes/{p_name}', process=process)

    def page(self, template, uri, **kwargs):
        async def generic_handler():
            return Response(template(self.app, **kwargs).render().encode())

        return MiyagiRoute(uri, ['GET', ], generic_handler)
