import os
import yaml


class DbTypes:
    SQLLITE = 'Sqllite'
    AWS = 'AWS'


class Config:
    statics = [os.path.join(os.getcwd(), 'Miyagi', 'web', 'static'), ]

    def __init__(self, file: str=None, obj: dict=None):
        if file:
            with open(file) as f:
                obj = yaml.load(f)
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
                DbTypes.AWS: f'{self.DB.engine}://{self.DB.user}:{self.DB.pwd}@{self.DB.uri}/{self.DB.dbname}',
                DbTypes.SQLLITE: f'{self.DB.type}:///{self.project_name.lower()}.db'
            }.get(self.DB.type)
        except KeyError:
            raise Exception('No db configuration found')

    @property
    def db_repo(self):
        return f'{self.project_name.lower()}_db_repo'
