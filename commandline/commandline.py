import os
from PyInquirer import prompt
from migrate.versioning import api

from .miyagi import App


class CommanlineController:
    def __init__(self, app: App):
        self.app = app


class DbController(CommanlineController):
    def create(self):
        responses = prompt([
            {
                'type': 'confirm',
                'name': 'yes',
                'message': f'Creating the database schema on {self.app.config.db_uri}. Do you want to continue?',
                'default': True
            }
        ])
        if responses['yes']:
            self.app.db.SQLAlchemyBase.metadata.create_all(self.app.db_engine)
            if not os.path.exists(self.app.config.db_repo):
                api.create(self.app.config.db_repo, 'database repository')
                api.version_control(self.app.config.db_uri, self.app.config.db_repo)
            else:
                api.version_control(self.app.config.db_uri,
                                    self.app.config.db_repo,
                                    api.version(self.app.config.db_repo))
