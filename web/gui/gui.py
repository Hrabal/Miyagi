# -*- coding: utf-8 -*-
from vibora.responses import Response
from vibora.request import Request
from vibora.hooks import Events

from tempy.widgets import TempyPage

from ..web import MiyagiRoute, MiyagiBlueprint
from .templates.main_pages import MiyagiAppHome, ProcessesPage, ProcessPage, ObjectEditPage


class Gui(MiyagiBlueprint):

    @property
    def endpoints(self):
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
                    ObjectEditPage,
                    f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{p_name}{self.app.config.OBJECTS_PX}/{obj.name.lower()}/<uid>',
                    handler='create_modify_object_handler',
                    methods=['GET', 'POST'],
                    process=process,
                    obj=obj
                )
                # TODO: object remove endpoint

                # TODO: object actions endpoints
                # Object class methods

            # TODO: process actions endopoints

        # TODO: System endpoints and controllers

    def page(self, template: TempyPage,
             uri: str,
             handler: str='generic_handler',
             methods: list=None,
             **kwargs):
        """Creates a MiyagiRoute with the given url and methods.
        Here are stored handlers blueprints.
        """
        async def generic_handler():
            """Generic Vibora/Miyagi handler:
            Instantiates the given template with kwargs, renders it and returns it"""
            return Response(template(self.app, **kwargs).render().encode())

        async def create_modify_object_handler(request: Request, uid: int):
            """Handler for forms:
            Instantiates the given template with kwargs, renders it and returns it"""
            obj = kwargs.get('obj')
            if request.method == b'GET':
                if uid:
                    inst = obj.cls.get(uid)
                else:
                    inst = obj.cls()
            elif request.method == b'POST':
                if uid:
                    inst = obj.cls.get(uid)
                else:
                    inst = obj.cls()
                form = await request.form()
                inst.set_dict(form)
                inst.save()
            kwargs['inst'] = inst
            return Response(template(self.app, **kwargs).render().encode())

        handler = self._copy_handler(locals().get(handler), kwargs)
        methods = methods or ['GET', ]
        return MiyagiRoute(uri, methods, handler)
