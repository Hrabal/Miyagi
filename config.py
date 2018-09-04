import os
import yaml
from .tools import MiyagiEnum


class DbTypes(MiyagiEnum):
    SQLLITE = 'sqlite'
    AWS = 'AWS'


class DBEngines(MiyagiEnum):
    POSTGRES = 'postgres'
    MYSQL = 'mysql'


class Config:
    statics = [os.path.join(os.getcwd(), 'Miyagi', 'web', 'static'), ]
    JSON_API_PX = '/jsnapi'
    GUI_PX = '/app'
    PROCESSES_PX = '/processes'
    OBJECTS_PX = '/objects'

    from_file = False

    def __init__(self, file: str=None, obj: dict=None):
        if file:
            try:
                with open(file) as f:
                    obj = yaml.load(f)
                    self.from_file = True
            except FileNotFoundError:
                print('WARNING!! No config file found! Using only defaults.')
                obj = {}
        for k, v in obj.items():
            if isinstance(v, dict):
                kls = type(k, (Config, ), v)
                setattr(self, k, kls(obj=v))
            else:
                if k == 'statics':
                    self.statics.extend(v)
                else:
                    setattr(self, k, v)
        self.project_name = os.getcwd().split('/')[-1]

    def __repr__(self):
        attr_repr = ', '.join(repr(v) if isinstance(v, Config)
                              else f'{k}={v}'
                              for k, v in self.__dict__.items())
        return f'{self.__class__.__name__}({attr_repr})'

    @property
    def db_uri(self):
        try:
            return {
                DbTypes.AWS.value: f'{self.DB.engine}://{self.DB.user}:{self.DB.pwd}@{self.DB.uri}/{self.DB.dbname}',
                DbTypes.SQLLITE.value: f'{self.DB.type}:///{self.project_name.lower()}.db'
            }.get(self.DB.type)
        except KeyError:
            raise Exception('No db configuration found')

    @property
    def db_repo(self):
        return f'{self.project_name.lower()}_db_repo'
