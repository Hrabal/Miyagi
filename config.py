# -*- coding: utf-8 -*-
import os
from ruamel import yaml
from .tools import MiyagiEnum


class DbTypes(MiyagiEnum):
    SQLLITE = 'sqlite'
    AWS = 'AWS'


class DBEngines(MiyagiEnum):
    POSTGRES = 'postgres'
    MYSQL = 'mysql'


class Config:
    """Miyagi Config object.
    Converts a yml or a dict into an object that can be accessed by attributes
    recursively.
    All attributes are class attributes so they don't change between app/config instances."""

    # Miyagi constants, those can be overwritten in config.yml
    statics = [os.path.join(os.getcwd(), 'Miyagi', 'web', 'static'), ]  # if more statics are given those will be added to this list
    JSON_API_PX = '/jsnapi'  # base uri path of the jsonapi
    GUI_PX = '/app'  # base uri path of the gui
    PROCESSES_PX = '/processes'  # path part of the processes in bot apis and gui
    OBJECTS_PX = '/objects'  # path part of the processe's objects in bot apis and gui

    _from_file = False

    def __init__(self, file: str=None, obj: dict=None):
        """Make a config from either a file or a dict.
        The file (path relative to cwd()) have precedence."""
        if file:
            try:
                with open(file) as f:
                    obj = yaml.load(f)
                    self._from_file = True
            except FileNotFoundError:
                print('WARNING!! No config file found! Using only defaults.')
                obj = {}
        # Recursive Config creation.
        # Dicts in the imput are converted in child Config objects
        # 'statics' keys are added to the self.statics
        for k, v in obj.items():
            if isinstance(v, dict):
                kls = type(k, (Config, ), v)
                setattr(self.__class__, k, kls(obj=v))
            else:
                if k == 'statics':
                    self.statics.extend(v)
                else:
                    setattr(self.__class__, k, v)
        self.project_name = os.getcwd().split('/')[-1]

    def __repr__(self):
        attr_repr = ', '.join(repr(v) if isinstance(v, Config)
                              else f'{k}={v}'
                              for k, v in self.__dict__.items())
        return f'{self.__class__.__name__}({attr_repr})'
