# -*- coding: utf-8 -*-
import os
import inspect
from pyfiglet import Figlet
from importlib import import_module

# Miyagi imports
from .config import Config
from .db import Db
from .web import WebApp


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

    def __init__(self, config: str=None, blueprints: list=None, for_web: bool=False):
        # Create the config object from the provided config file
        self.config = Config(config)

        print()
        print(Figlet(font='colossal').renderText('Miyagi'), f'App name: {self.config.project_name}')

        # Read the project processes
        self._read_processes()

        # Init the db
        self.db = Db(self.config)

        if for_web:
            # init the webapp
            self.webapp = WebApp(self)

            # Add extra Vibora blueprints
            # TODO: exception handling, and check that every blueprint is a valid vIbora Blueprint instance
            blueprints = blueprints or []
            for blueprint in blueprints:
                self.webapp.vibora.add_blueprint(blueprint)

    def run(self):
        """Wrapper around Vibora's run method"""
        self.webapp.vibora.run(host=self.config.host, port=self.config.port, debug=self.config.debug)

    def _read_processes(self):
        """Traverses the "processes" folder and adds all the found valid processes to the Miyagi app
        TODO: processes validation"""
        print('\nLoading installed processes...')
        self.processes = {}
        for p_name in os.listdir('./processes'):
            # For each valid folder..
            if os.path.isdir(os.path.join('.', 'processes', p_name)) and not p_name.startswith('__'):
                # Add the process as a Miyagi.MiyagiProcess instance to the app's processes
                process = MiyagiProcess(p_name, import_module(f'processes.{p_name}', '..processes'))
                self.processes[p_name] = process
        print(f'Loaded Processes: {", ".join(map(str, self.processes.values()))}')
        print(f'Loaded Objects: {", ".join(map(str,  (o for p in self.processes.values() for o in p.objects)))}')


class MiyagiObject:
    """Class that wraps a class into process object.
    Reads the object and finds out all the Miyagi configurations in the provided class
    """

    def __init__(self, obj, parent=None):
        self.name = obj.__name__
        self._gui = getattr(obj, '_gui', True)
        self._json_api = getattr(obj, '_json_api', False)
        self.parent = parent

        # inspect the class to find nested objects
        self._objects = {}
        for name, sub_obj in inspect.getmembers(obj, inspect.isclass):
            if sub_obj != type:
                sub_obj = MiyagiObject(sub_obj, parent=self)
                self._objects[sub_obj.name] = sub_obj

        # Make a SQLAlchemy model out of this class
        self.cls = Db.craft_sqalchemy_model(obj, '_'.join(part.name.lower() for part in self.path))

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


class MiyagiProcess:
    """Class that wraps a process module.
    Reads the module folder and extracts all the useful infos for later use.
    """

    def __init__(self, name, module):
        self.name = name
        self.module = module
        self.icon = getattr(module, 'icon', 'fa-code-branch')  # Default icon

        # Read all the object classes from this module
        self._read_objects()

    def _read_objects(self):
        """Reads a module in search for valid Miyagi objects to add."""
        self._objects = []
        # For every class in this module..
        for name, obj in inspect.getmembers(self.module, inspect.isclass):
            # ..if it's a class defined in the process and not imported from elsewhere..
            # TODO: better validation
            if getattr(obj, '__module__', None) == f'{self.module.__name__}.objects':
                # ..f it's not type..
                if obj != type:
                    self._digest_object(obj)  # ..make a MiyagiObject instance.

    def _digest_object(self, obj):
        """Make a MiyagiObject instance from a class and add it to this process's objects."""
        obj = MiyagiObject(obj)
        self._objects.append(obj)

    @property
    def objects(self):
        """Iterate all this processes MiyagiObjects"""
        for base_obj in self._objects:
            for obj in base_obj.objects:
                yield obj  # First yielded item here is base_obj itself, then all the base_obj's nested classes

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.name}>'
