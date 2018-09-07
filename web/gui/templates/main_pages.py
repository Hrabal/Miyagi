# -*- coding: utf-8 -*-
from tempy.tags import *

from .base import MiyagiBase


class MiyagiAppHome(MiyagiBase):
    @property
    def page_title(self):
        return self.app.config.project_name

    def init(self):
        self.content('Home Page')


class ProcessesPage(MiyagiBase):
    @property
    def page_title(self):
        return 'Processes'

    def init(self):
        self.content(
            Div(klass='table-responsive')(
                Table(id="processesTable", klass="table table-striped")(
                    Thead()(
                        Th()(
                            Input(type="checkbox", id="checkall")
                        ),
                        Th()(''),
                        Th()('Process Name'),
                        Th()('Todos'),
                        Th()('Active Users'),
                        Th()('Process Actions'),
                    ),
                    Tbody()(
                        Tr(klass='danger' if process.is_admin else '')(
                            Td()(
                                Input(type="checkbox", klass="checkthis")
                            ),
                            Td()(
                                A(href=f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{process.name.lower()}')(
                                    I(klass=f'fas {process.icon}')
                                )
                            ),
                            Td()(
                                A(href=f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{process.name.lower()}')(
                                    process.name.title()
                                )
                            ),
                            Td()(''),
                            Td()('1'),
                            Td()('New - Merge'),
                        ) for _, process in self.app.processes.items()
                    )
                )
            )
        )


class ProcessPage(MiyagiBase):
    def __init__(self, *args, **kwargs):
        self.process = kwargs.pop('process')
        super().__init__(*args, **kwargs)

    @property
    def page_title(self):
        return self.process.name.title()

    @property
    def process_uri(self):
        return f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{self.process.name}'

    def init(self):
        self.content(
            Table(klass='table table-striped')(
                Tr()(
                    Td(colspan=3)(
                        H6(klass='border-bottom border-gray pb-2 mb-0')('Process Objects')
                    )
                ),
                [Tr()(
                    Td()(I(klass='fas fa-th-list')),
                    Td()(A(href=f'{self.process_uri}{self.app.config.OBJECTS_PX}/{obj.name.lower()}/add')(
                        I(klass='fas fa-plus-square'))
                    ),
                    Td()(P()(obj.name.title()))
                ) for obj in self.process.objects]
            )
        )


class ObjectAddPage(MiyagiBase):
    def __init__(self, *args, **kwargs):
        self.process = kwargs.pop('process')
        self.obj = kwargs.pop('obj')
        super().__init__(*args, **kwargs)

    @property
    def page_title(self):
        return f'Create new {self.obj.name.title()}'

    def init(self):
        self.content(
            Div(klass='container')(Form(action=f'{self.app.config.GUI_PX}{self.app.config.PROCESSES_PX}/{self.process.name}{self.app.config.OBJECTS_PX}/{self.obj.name.lower()}/add', method="POST")(
                [Div(klass='form-group row')(
                    Label(klass='col-2 col-form-label', **{'for': f'{self.obj.name}{k.title()}'})(
                        k.title()
                    ),
                    Div(klass="col-10")(
                        Input(id=f'{self.obj.name}{k.title()}', klass="form-control", typ="text")()
                    )
                ) for k, v in self.obj.cls().items(system_attributes=False)],
                Div(klass='form-group row')(
                    Button(typ="submit", klass="btn btn-primary")('Save')
                )
            ))
        )
