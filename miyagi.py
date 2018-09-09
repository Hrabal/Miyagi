# -*- coding: utf-8 -*-
import inspect
from itertools import chain, zip_longest
from pyfiglet import Figlet
from types import ModuleType

from vibora.blueprints import Blueprint

# Miyagi imports
from .config import Config
from .db import Db
from .web import WebApp
from .tools import objdict
from .tools import import_miyagi_modules


# Exceptions import
from .exceptions import MiyagiTypeError


class App:
    """
    Miyagi App class, is intended to be the main Miyagi enviroment class.
    It contains a db instance so every object that can access an App instance can use the db.
    It contains and manages the webapp class, so it can work directly on the Vibora server.

    This is the main entry point to work inside a Miyagi installation, can be imported and used
    from the Python interpreter, it's used by the Miyagi commandline tool, and it's the Class that
    have to be instantiated to run the web server,

    Main tasks are:
    - read the Miyagi project folders and find processes to add
    - init the db connection
    - init the webserver
    - add custom project Vibora blueprints
    """

    def __init__(self, config: str=None, custom_pages: list=None, for_web: bool=False):

        print()
        print(Figlet(font='colossal').renderText('Miyagi'))

        # Create the config object from the provided config file
        self.config = Config(config)
        print(f'App name: {self.config.project_name}')

        # Read the project processes
        self._read_processes()
        # Init the db
        self.db = Db(self.config)
        # Bind the Db instance to this app's processes and make the SQLAlchemy models
        self.db.digest_objects(self.objects)

        if for_web:
            self.init_webapp(custom_pages=custom_pages)

    @property
    def objects(self):
        """Iterator that yields all the App's objects from all the App's processes."""
        for _, proc in self.processes.items():
            yield from proc.objects

    def init_webapp(self, custom_pages: list=None):
        """Creates the WebApp instance and adds the given custom Vibora Blueprints."""
        # init the webapp
        self.webapp = WebApp(self)
        if custom_pages:
            self.add_blueprints(custom_pages)

    def add_blueprints(self, blueprints: list):
        # Add extra Vibora blueprints
        # TODO: exception handling, and check that every blueprint is a valid Vibora Blueprint instance
        # Registering extra/custom components
        for blueprint in blueprints:
            if not isinstance(blueprint, Blueprint):
                raise MiyagiTypeError(obj=blueprint, expected=Blueprint, par='custom_pages')

            print('\nAdding custom installation routes:')
            self.webapp.vibora.add_blueprint(blueprint)
            for route in blueprint.routes:
                print(route)

    def run(self):
        """Wrapper around Vibora's run method"""
        self.webapp.vibora.run(host=self.config.host, port=self.config.port, debug=self.config.debug)

    def _read_processes(self, folders: list=None):
        """Traverses a folder looking for processes and adds all the valid processes to the Miyagi app.
        If no folder is given, default folders are used:
        - <Project folder>/processes
        - <Miyagi folder>/processes'"""
        if folders:
            # Convert the dirs to import function args
            import_kargs = map(dict(zip_longest(('base_dir', ), folders)))
        else:
            import_kargs = ({'internal': True}, {'base_dir': './processes'})

        self.processes = objdict()
        for kwargs in import_kargs:
            print(f'\nLoading{" Miyagi internal " if "internal" in kwargs else " project "}processes...')
            # Call the import function with either the internal flag or the process directory
            for module in import_miyagi_modules(**kwargs):
                # Add the process as a Miyagi.MiyagiProcess instance to the app's processes
                p_name = module.__name__.split('.')[-1]
                process = MiyagiProcess(p_name, module)
                self.processes[p_name] = process
        print(f'\nLoaded Processes: {", ".join(map(str, self.processes.values()))}')
        print(f'Loaded Objects: {", ".join(map(str,  (o for p in self.processes.values() for o in p.objects)))}')


class MiyagiObject:
    """Class that wraps a class into process object.
    Reads the object and finds out all the Miyagi configurations in the provided class
    """

    def __init__(self, obj: type, parent=None):
        self.name = obj.__name__
        self._gui = getattr(obj, '_gui', True)
        self._json_api = getattr(obj, '_json_api', False)
        self.parent = parent
        self._original_cls = obj

        # inspect the class to find nested objects
        self._objects = {}
        for _, sub_obj in inspect.getmembers(obj, inspect.isclass):
            if sub_obj != type:
                sub_obj = MiyagiObject(sub_obj, parent=self)
                self._objects[sub_obj.name] = sub_obj

    @property
    def objects(self):
        """Iterator for the object and all the nested objects"""
        yield self  # First yield is the object itself
        for _, obj in self._objects.items():
            yield from obj.objects  # yield from the same method of the nested object

    @property
    def reverse_path(self):
        """Iterator that yields the object's hierarchy starting from the object itself,
        going up traversing the parents. child2 -> child1 -> root"""
        parent = self
        while parent:  # A base object have parent == None so it stops
            yield parent
            parent = parent.parent

    @property
    def path(self):
        """Reverses the reverse_path iterator (I know..).
        Yields a path from root to leaf."""
        return reversed(list(self.reverse_path))

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'


class MiyagiAction:
    """Class that wraps actions classes"""
    pass


class MiyagiProcess:
    """Class that wraps a process module.
    Reads the module folder and extracts all the useful infos for later use.
    """

    def __init__(self, name: str, module: ModuleType):
        self.name = name
        self.module = module
        self.icon = getattr(module, 'icon', 'fa-code-branch')  # Default icon
        self.is_admin = module.__package__.startswith('Miyagi')

        # Read all the object classes from this module
        for module, cls in [
            ('objects', MiyagiObject),
        ]:
            self._read_element(module, cls)

    def _get_module_element(self, typ: str):
        # For every class in this module..
        for _, obj in inspect.getmembers(self.module, inspect.isclass):
            # ..if it's a class defined in the process and not imported from elsewhere..
            if getattr(obj, '__module__', None) == f'{self.module.__name__}.{typ}':
                # ..if it's not type..
                if obj != type:
                    yield obj

    def _read_element(self, module: ModuleType, cls: type):
        """Reads a module in search for valid Miyagi objects to add."""
        elements = []
        # For every class in this module..
        for obj in self._get_module_element(module):
            # TODO: better validation
            obj = cls(obj)  # ..make a MiyagiXXX instance.
            elements.append(obj)
        setattr(self, f'_{module}', elements)

    @property
    def objects(self):
        """Iterate all this processes MiyagiObjects"""
        for base_obj in self._objects:
            for obj in base_obj.objects:
                yield obj  # First yielded item here is base_obj itself, then all the base_obj's nested classes

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'
