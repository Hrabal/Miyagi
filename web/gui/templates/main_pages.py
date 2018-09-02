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
                Table(id="processesTable", klass="table table-bordred table-striped")(
                    Thead()(
                        Th()(Input(type="checkbox", id="checkall")),
                        Th()(''),
                        Th()('Process Name'),
                        Th()('Todos'),
                        Th()('Active Users'),
                        Th()('Process Actions'),
                    ),
                    Tbody()(
                        Tr(klass='danger' if process.is_admin else '')(
                            Td()(Input(type="checkbox", klass="checkthis")),
                            Td()(A(href=f'/app/processes/{process.name.lower()}')(I(klass=f'fas {process.icon}'))),
                            Td()(A(href=f'/app/processes/{process.name.lower()}')(process.name.title())),
                            Td()(''),
                            Td()('1'),
                            Td()('New - Merge'),
                        ) for _, process in self.app.processes.items()
                    )
                )
            )
        )


class ProcessPage(MiyagiBase):
    @property
    def page_title(self):
        return self.process.name.title()

    def __init__(self, *args, **kwargs):
        self.process = kwargs.pop('process')
        super().__init__(*args, **kwargs)

    def init(self):
        self.content(
            Table(klass='table table-striped')(
                Tr()(
                    Td(colspan=3)(
                        H6(klass='border-bottom border-gray pb-2 mb-0')('Process Objects')
                    )
                ),
                [Tr()(
                    Td()(I(klass='far fa-th-list')),
                    Td()(I(klass='fas fa-plus-square')),
                    Td()(P()(obj.name.title()))
                ) for obj in self.process.objects]
            )
        )
