# -*- coding: utf-8 -*-
from tempy.tags import Div, Table, Thead, Th, Input, Tbody, Tr, Td, I, A

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
            
        )
