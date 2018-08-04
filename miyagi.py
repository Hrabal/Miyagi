import os
import inspect
from pyfiglet import Figlet
from importlib import import_module

from vibora import Vibora
from vibora.blueprints import Blueprint

from .config import Config
from .db import Db


class App:
    def __init__(self, config: str=None, blueprints: list=None, as_script: bool=False):
        self.config = Config(config)
        print()
        print(Figlet(font='colossal').renderText('Miyagi'), f'App name: {self.config.project_name}')
        self._read_processes()
        self.db = Db(self.config)

        if not as_script:
            self.webapp = Vibora()
            self.webapp.components.add(self)
            blueprints = blueprints or []

            self._make_gui()
            self._make_json_api()

            for blueprint in blueprints:
                self.webapp.add_blueprint(blueprint)

    def run(self):
        self.webapp.run(host=self.config.host, port=self.config.port, debug=self.config.debug)

    def _make_json_api(self):
        print('\nInitializing JsonApi routes:')
        from .web.apis.jsonapi import JsonApi

        self.json_api = Blueprint()
        for route in JsonApi(self).craft():
            self._add_route(self.json_api, route)
        self.webapp.add_blueprint(self.json_api)

    def _make_gui(self):
        print('\nInitializing Web frontend:')
        from .web.frontend import Gui

        self.web = Blueprint()
        for route in Gui(self).craft():
            self._add_route(self.web, route)
        self.webapp.add_blueprint(self.web)

    def _add_route(self, blueprint, route):
        print(f'Adding route: {self.webapp.url_scheme}://{self.config.host}:{self.config.port}{route.uri}')
        blueprint.route(route.uri, methods=route.methods)(route.handler)

    def _read_processes(self):
        print('\nLoading installed processes...')
        self.processes = {}
        for p_name in os.listdir('./processes'):
            if os.path.isdir(os.path.join('.', 'processes', p_name)) and not p_name.startswith('__'):
                process = MiyagiProcess(p_name, import_module(f'processes.{p_name}', '..processes'))
                self.processes[p_name] = process
        print(f'Loaded Processes: {", ".join(map(str, self.processes.values()))}')
        print(f'Loaded Objects: {", ".join(map(str,  (o for p in self.processes.values() for o in p.objects)))}')


class MiyagiObject:
    def __init__(self, obj, parent=None):
        self.name = obj.__name__
        self._gui = getattr(obj, '_gui', True)
        self._json_api = getattr(obj, '_json_api', False)
        self.parent = parent
        self._objects = {}
        for name, sub_obj in inspect.getmembers(obj, inspect.isclass):
            if sub_obj != type:
                sub_obj = MiyagiObject(sub_obj, parent=self)
                self._objects[sub_obj.name] = sub_obj
        self.cls = Db.craft_sqalchemy_model(obj, '_'.join(part.name.lower() for part in self.path))

    @property
    def objects(self):
        yield self
        for _, obj in self._objects.items():
            yield from obj.objects

    @property
    def reverse_path(self):
        parent = self
        while parent:
            yield parent
            parent = parent.parent

    @property
    def path(self):
        return reversed(list(self.reverse_path))

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'


class MiyagiProcess:
    def __init__(self, name, module):
        self.name = name
        self.module = module
        self._objects = []
        for name, obj in inspect.getmembers(self.module, inspect.isclass):
            if getattr(obj, '__module__', None) == f'{self.module.__name__}.objects':
                if obj != type:
                    obj = MiyagiObject(obj)
                    self._objects.append(obj)

    @property
    def objects(self):
        for base_obj in self._objects:
            for obj in base_obj.objects:
                yield obj

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'
