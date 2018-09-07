# -*- coding: utf-8 -*-
from vibora.responses import Response

from ...miyagi import App
from ..web import MiyagiRoute, MiyagiBlueprint
from .templates.main_pages import MiyagiAppHome, ProcessesPage, ProcessPage, ObjectAddPage


class Gui(MiyagiBlueprint):

    @property
    def pages(self):
        """Generator of all the GUI pages.
        Pages a MiyagiRoutes: containers of handler functions, methods and infos
        """
        # Yields the home page
        yield self.page(MiyagiAppHome, self.app.config.GUI_PX)
        # Yields the process list page
        yield self.page(ProcessesPage, f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}')

        for p_name, process in self.app.processes.items():
            # For every process yields the relative general page
            yield self.page(
                ProcessPage,
                f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{p_name}',
                process=process
            )
            for obj in process.objects:
                # For every object in the process yields the relative page
                # TODO: object page
                # List of instances + general object actions

                # For every object in the process yields the object creation form
                yield self.page(
                    ObjectAddPage,
                    f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{p_name}{self.app.config.OBJECTS_PX}/{obj.name.lower()}/add',
                    process=process,
                    obj=obj
                )
                # TODO: object remove endpoint

                # TODO: object actions endpoints
                # Object class methods

            # TODO: process actions endopoints

        # TODO: System endpoints and controllers

    def page(self, template, uri, methods=None, **kwargs):
        """Definition of a generic Vibora handler function.
        """

        async def generic_handler():
            """Generic Vibora/Miyagi handler:
             Instantiates the given template with kwargs, renders it and returns it"""
            return Response(template(self.app, **kwargs).render().encode())
        methods = methods or ['GET', ]
        return MiyagiRoute(uri, methods, generic_handler)
