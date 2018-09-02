# -*- coding: utf-8 -*-
from tempy.widgets import TempyPage
from tempy.tags import Meta, Title, Nav, Div, A, Input, Ul, Li, Span, I, H6, H1, Main

from ....miyagi import App

from .resources import Bootstrap4, FontAwesome, JQuery, MainCSS, Popper


class MiyagiBase(TempyPage):

    def __init__(self, app: App):
        self.app = app
        self.breadcrumb = ''
        super().__init__()

    @property
    def page_title(self):
        return ''

    def js(self):
        return [JQuery.js, Popper.js, Bootstrap4.js, ]

    def css(self):
        return [Bootstrap4.css, FontAwesome.css, MainCSS.css]

    def init(self):
        self.head(self.css())
        self.head(
            Meta(charset="utf-8"),
            Meta(name="viewport",
                 content="width=device-width, initial-scale=1, shrink-to-fit=no"),
            Title()(f'{self.app.config.project_name} - {self.page_title}')
        )
        self.content_title = Div(klass='d-flex justify-content-between flex-wrap '
                                 'flex-md-nowrap align-items-center pb-2 mb-3 border-bottom')(
            H1(klass='h2')(self.page_title),
            self.breadcrumb
        )
        self.content = Div(klass='d-flex justify-content-between flex-wrap pb-2 mb-3 flex-md-nowrap')
        self.body(
            Nav(klass='navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0')(
                A(klass='navbar-brand col-sm-3 col-md-2 mr-0', href='/app')(self.app.config.project_name),
                Input(klass='form-control form-control-dark w-100',
                      typ='text',
                      placeholder='Search',
                      **{'aria-label': 'Search'}),
                Ul(klass='navbar-nav px-3')(
                    Li(klass='nav-item text-nowrap')(
                        A(klass='nav-link', href='/signout')('Sign out')
                    )
                )
            ),
            Div(klass="container-fluid")(
                Div(klass='row')(
                    Nav(klass='col-md-2 d-none d-md-block bg-light sidebar')(
                        Div(klass='sidebar-sticky')(
                            Ul(klass='nav flex-column')(
                                Li(klass='nav-item')(
                                    A(klass='nav-link active', href='/app')(
                                        I(klass='fas fa-home'),
                                        ' Dashboard',
                                        Span(klass='sr-only')('(current)')
                                    )
                                ),
                                Li(klass='nav-item sidebar-heading d-flex justify-content-between '
                                         'align-items-center px-3 mt-4 mb-1 text-muted')(
                                    A(klass='nav-link', href='/app/processes')(
                                        I(klass="fas fa-chalkboard-teacher"),
                                        ' Processes ',
                                    ),
                                    A(klass='navbar-toggler collapsed',
                                      **{
                                            "data-toggle": "collapse",
                                            "data-target": "#processesList",
                                            "aria-expanded": "false"})(
                                        I(klass="fas fa-plus-circle navbar-toggler-icon")
                                    )
                                ),
                                Div(klass="collapse", id="processesList")(
                                    Ul(klass="nav flex-column")(
                                        Li(klass='nav-item')(
                                            A(href=f'/app/processes/{process.name.lower()}', klass='nav-link')(
                                                I(klass=f'fas {process.icon}'), ' ' + process.name.title()
                                            )
                                        ) for process in self.app.processes.values()
                                    )
                                )
                            ),
                            H6(klass='sidebar-heading d-flex justify-content-between '
                                     'align-items-center px-3 mt-4 mb-1 text-muted')(
                                Span()('Saved Links')
                            ),
                        )
                    ),
                    Main(role='main', klass='col-md-9 ml-sm-auto col-lg-10 pt-3 px-4')(
                        self.content_title, self.content
                    )
                )
            ),
            self.js()
        )
