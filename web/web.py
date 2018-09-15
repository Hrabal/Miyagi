# -*- coding: utf-8 -*-
from types import FunctionType

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

    def _copy_handler(self, f, kwargs):
        fname = '_'.join(getattr(v, 'name', v.__class__.__name__) for v in kwargs.values())
        """Creates a copy of the given handler and injects the kwargs as func variables"""
        fn = FunctionType(f.__code__, f.__globals__, f'{f.__name__}_{fname}', f.__defaults__, f.__closure__)
        # in case f was given attrs (note this dict is a shallow copy):
        fn.__dict__.update(f.__dict__)
        # Inject the route kwargs
        fn.__dict__.update(kwargs)
        # Copy the type hints so Vibora can optimize stuff
        fn.__annotations__ = f.__annotations__
        return fn


class WebApp:
    def __init__(self, app):
        self.app = app
        print('\nInitializing Vibora webapp.')
        self.vibora = Vibora(
            static=StaticHandler(  # Add the statics handler
                paths=self.app.config.statics,
                url_prefix='/static',
                max_cache_size=1 * 1024 * 1024
            )
        )
        print(f'Added static folders: {self.app.config.statics}')

        # Miyagi app and config should be avaiable in every handler
        self.vibora.components.add(self.app)
        self.vibora.components.add(self.app.config)

        # Make all the Miyagi webapp components
        self._make_gui()
        self._make_json_api()

    def _make_json_api(self):
        print('\nInitializing JsonApi routes:')
        # Import in function for it's a circular import
        from .apis.jsonapi import JsonApi
        self._make_blueprint('json_api', JsonApi)

    def _make_gui(self):
        print('\nInitializing Web frontend:')
        # Import in function for it's a circular import
        from .gui import Gui
        self._make_blueprint('web', Gui)

    def _make_blueprint(self, bp_name: str, bp: MiyagiBlueprint):
        # Make a blueprint
        vibora_bp = Blueprint()
        # Make it accessible in self
        setattr(self, bp_name, vibora_bp)
        # get all the routes in the given MiyagiBlueprint
        for route in bp(self.app).endpoints:
            # Register the route in the new blueprint
            self._add_route(vibora_bp, route)
        # Register the Blueprint in the Vibora App
        self.vibora.add_blueprint(vibora_bp)

    def _add_route(self, blueprint: Blueprint, route: MiyagiRoute):
        print(f'Adding route: {self.vibora.url_scheme}://{self.app.config.host}:{self.app.config.port}{route.uri}')
        # Call the Vibora blueprint's decorator
        blueprint.route(route.uri, methods=route.methods)(route.handler)
