from tempy.widgets import TempyPage
from tempy.tags import Meta, Title, Nav, Div, A, Input, Ul, Li, Span, I, H6, H1, Main

from ....miyagi import App

from .resources import Bootstrap4, FontAwesome, JQuery, MainCSS


class MiyagiBase(TempyPage):
    def __init__(self, app: App, title: str=''):
        self.app = app
        self.page_title = title
        super().__init__()

    def js(self):
        return [JQuery.js, Bootstrap4.js, ]

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
        self.content = Div(klass='d-flex justify-content-between flex-wrap '
                           'flex-md-nowrap align-items-center pb-2 mb-3 border-bottom')(
            H1(klass='h2')(self.page_title)
        )
        self.body(
            Nav(klass='navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0')(
                A(klass='navbar-brand col-sm-3 col-md-2 mr-0', href='/app')(self.app.config.project_name),
                Input(klass='form-control form-control-dark w-100',
                      typ='text',
                      placeholder='Search',
                      **{'aria-label': 'Search'}),
                Ul(klass='navbar-nav px-3')(
                    Li(klass='nav-item text-nowrap')(
                        A(klass='nav-link')('Sign Out')
                    )
                )
            ),
            Div(klass="container-fluid")(
                Div(klass='row')(
                    Nav(klass='col-md-2 d-none d-md-block bg-light sidebar')(
                        Div(klass='sidebar-sticky')(
                            Ul(klass='nav flex-column')(
                                Li(klass='nav-item')(
                                    A(klass='nav-link active', href='Dashboard')(
                                        I(klass='fas fa-home'),
                                        ' Dashboard',
                                        Span(klass='sr-only')('(current)')
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
                        self.content
                    )
                )
            ),
            self.js()
        )
