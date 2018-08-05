# -*- coding: utf-8 -*-
"""
Collection of all the command line controllers we're gonna provide to the command line utility of Miyagi.
"""
import os
from PyInquirer import prompt, Separator

from migrate.versioning import api
from migrate.exceptions import DatabaseAlreadyControlledError

from ..miyagi import App

from .colors import CEND, CRED

from .files import AppFiles


class CommanlineController:
    """Base class for commandline parsers"""

    def __init__(self, app: App):
        self.app = app


class InitController(CommanlineController):
    """Controller for the installation-specific tasks:
    - project initialization
    - project configuration
    """
    _callable = True
    _command = 'init'

    def project(self):
        yes = prompt([
            {
                'type': 'confirm',
                'name': 'yes',
                'message': f'Initializating a Miyagi project on: {os.getcwd()}. Do you want to continue?',
                'default': True
            }
        ])
        if yes['yes']:
            responses = prompt([
                {
                    'type': 'checkbox',
                    'name': 'todo',
                    'message': f'Please select the elements you want to init:',
                    'choices': [
                        Separator('= APP ='),
                        {
                            'name': 'Base Project',
                            'checked': True
                        },
                        {
                            'name': 'Virtual Envelope',
                        },
                        {
                            'name': 'Config File',
                        },
                        {
                            'name': 'Admin User',
                        },
                        {
                            'name': 'Custom routes'
                        },
                        {
                            'name': 'Example process'
                        },
                        Separator('= DB ='),
                        {
                            'name': 'Db creation'
                        },
                    ]
                }
            ])
            if 'Base Project' in responses['todo']:
                custom_extra = AppFiles.custom if 'Custom routes' in responses['todo'] else ('', '')
                with open('run.py', 'w') as f:
                    f.write(AppFiles.run % custom_extra)


class DbController(CommanlineController):
    """Controller for the installation-specific tasks:
    - init the db
    - upgrade, migrate, downgrade the db
    """
    _callable = True
    _command = 'db'

    def create(self):
        yes = prompt([
            {
                'type': 'confirm',
                'name': 'yes',
                'message': f'Creating the database schema on {self.app.config.db_uri}. Do you want to continue?',
                'default': True
            }
        ])
        if yes['yes']:
            self.app.db.SQLAlchemyBase.metadata.create_all(self.app.db.db_engine)
            repo_path = os.path.join(os.getcwd(), self.app.config.db_repo)
            try:
                if not os.path.exists(repo_path):
                    api.create(self.app.config.db_repo, 'database repository')
                    api.version_control(self.app.config.db_uri, self.app.config.db_repo)
                else:
                    api.version_control(self.app.config.db_uri,
                                        self.app.config.db_repo,
                                        api.version(self.app.config.db_repo))
            except DatabaseAlreadyControlledError:
                print(f'{CRED}ERROR!{CEND} Your database appear to be already initializated on version control.')
                print(f'Please check your db versioning tables and the db repository folder: {repo_path}')
                print('If everything looks ok, you either have to use the "db migrate" or the "db upgrade" commands.')
                print()
