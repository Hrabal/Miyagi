# -*- coding: utf-8 -*-
from vibora.responses import Response
from vibora.request import Request

from tempy.widgets import TempyPage

from ..web import MiyagiRoute, MiyagiBlueprint
from .templates.main_pages import MiyagiAppHome, ProcessesPage, ProcessPage, ObjectPage, ObjectEditPage


class Gui(MiyagiBlueprint):

    @property
    def endpoints(self):
        """Generator of all the GUI pages.
        Pages a MiyagiRoutes: containers of handler functions, methods and infos
        """

        # Yields the home page
        gui_uri = self.app.config.GUI_PX
        yield self.page(MiyagiAppHome, gui_uri)

        # Yields the process list page
        processes_uri = f'{gui_uri}{self.app.config.PROCESSES_PX}'
        yield self.page(ProcessesPage, processes_uri)

        for p_name, process in self.app.processes.items():
            # For every process yields the relative general page
            process_uri = f'{processes_uri}/{p_name}'
            yield self.page(
                ProcessPage,
                process_uri,
                process=process
            )
            for obj in process.objects:
                # For every object in the process yields the relative page
                # List of instances + general object actions
                object_uri = f'{process_uri}{self.app.config.OBJECTS_PX}/{obj.name.lower()}'
                yield self.page(
                    ObjectPage,
                    object_uri,
                    handler='generic_handler',
                    methods=['GET', ],
                    process=process,
                    obj=obj
                )

                # For every object in the process yields the object creation form
                yield self.page(
                    ObjectEditPage,
                    f'{object_uri}/<uid>',
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
            session = self.app.db.session()
            if request.method == b'GET':
                if uid:
                    inst = session.query(obj.cls).filter_by(uid=uid).first()
                    if not inst:
                        # TODO: raise
                        inst = obj.cls.new()
                else:
                    inst = obj.cls.new()
            elif request.method == b'POST':
                if uid:
                    inst = session.query(obj.cls).filter_by(uid=uid).first()
                else:
                    inst = obj.cls.new()
                form = await request.form()
                inst.set_dict(form)
                inst.save()
            kwargs['inst'] = inst
            return Response(template(self.app, **kwargs).render().encode())

        handler = self._copy_handler(locals().get(handler), kwargs)
        methods = methods or ['GET', ]
        return MiyagiRoute(uri, methods, handler)
