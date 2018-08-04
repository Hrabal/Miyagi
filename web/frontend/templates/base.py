from tempy.widgets import TempyPage
from tempy.tags import Meta, Div, Title, Header, Footer, Aside, Main

from .resources import Bootstrap4, FontAwesome, JQuery


class MiyagiBase(TempyPage):
    def js(self):
        return [JQuery.js, Bootstrap4.js, ]

    def css(self):
        return [Bootstrap4.css, FontAwesome.css, ]

    def init(self):
        self.head(self.css(), self.js())
        self.head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1, shrink-to-fit=no"),
            Title()("Miyagi!")
        )
        self.body.attr(**{"klass": "sidebar-show aside-menu-show header-fixed footer-fixed"})
        self.body(
            Header(klass="app-header navbar")('Miyagi!'),
            Div(klass="app-body")(
                Div(klass="sidebar")('Side1'),
                Main(klass="main")("Here is some Content"),
                Aside(klass="aside-menu")('Side2')
            ),
            Footer(klass="app-footer")('Footer'),
        )
