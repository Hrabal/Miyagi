# -*- coding: utf-8 -*-
from vibora.responses import Response

from ...miyagi import App
from ..web import MiyagiRoute
from .templates.main_pages import MiyagiAppHome, ProcessesPage, ProcessPage, ObjectAddPage


class Gui:
    def __init__(self, app: App):
        self.app = app

    @property
    def pages(self):
        yield self.page(MiyagiAppHome, self.app.config.GUI_PX)
        yield self.page(ProcessesPage, f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}')
        for p_name, process in self.app.processes.items():
            yield self.page(
                ProcessPage,
                f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{p_name}',
                process=process
            )
            for obj in process.objects:
                yield self.page(
                    ObjectAddPage,
                    f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{p_name}{self.app.config.OBJECTS_PX}/{obj.name.lower()}/add',
                    process=process,
                    obj=obj
                )

    def page(self, template, uri, **kwargs):
        async def generic_handler():
            return Response(template(self.app, **kwargs).render().encode())

        return MiyagiRoute(uri, ['GET', ], generic_handler)
