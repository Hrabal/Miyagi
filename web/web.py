# -*- coding: utf-8 -*-
from vibora import Vibora
from vibora.blueprints import Blueprint
from vibora.static import StaticHandler


class MiyagiRoute:
    def __init__(self, uri: str, methods: list, fnc):
        self.uri = uri
        self.methods = methods
        self.handler = fnc


class MiyagiBlueprint:
    def __init__(self, app):
        self.app = app


class WebApp:
    def __init__(self, app):
        self.app = app
        print('\nInitializing Vibora webapp.')
        self.vibora = Vibora(
            static=StaticHandler(
                paths=self.app.config.statics,
                url_prefix='/static',
                max_cache_size=1 * 1024 * 1024
            )
        )
        self.vibora.components.add(self.app)
        self.vibora.components.add(self.app.config)
        print(f'Added static folders: {self.app.config.statics}')
        self._make_gui()
        self._make_json_api()

    def _make_json_api(self):
        print('\nInitializing JsonApi routes:')
        from .apis.jsonapi import JsonApi

        self.json_api = Blueprint()
        for route in JsonApi(self.app).endpoints:
            self._add_route(self.json_api, route)
        self.vibora.add_blueprint(self.json_api)

    def _make_gui(self):
        print('\nInitializing Web frontend:')
        from .gui import Gui

        self.web = Blueprint()
        for route in Gui(self.app).pages:
            self._add_route(self.web, route)
        self.vibora.add_blueprint(self.web)

    def _add_route(self, blueprint: Blueprint, route: MiyagiRoute):
        print(f'Adding route: {self.vibora.url_scheme}://{self.app.config.host}:{self.app.config.port}{route.uri}')
        blueprint.route(route.uri, methods=route.methods)(route.handler)
