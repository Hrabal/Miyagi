# -*- coding: utf-8 -*-
"""
Collection of all the command line controllers we're gonna provide to the command line utility of Miyagi.
"""
import os
import traceback
from ruamel import yaml
from PyInquirer import prompt, Separator

from migrate.versioning import api
from migrate.exceptions import DatabaseAlreadyControlledError

from ..miyagi import App
from ..config import DbTypes, DBEngines

from .colors import CEND, CRED
from .constants import ProjectInitOptions
from .validators import NumberValidator

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
    callable_cls = True
    command = 'project'

    def init(self):
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
                            'name': ProjectInitOptions.BASE_PROJECT,
                            'checked': True
                        },
                        {
                            'name': ProjectInitOptions.VIRTUAL_ENVELOPE,
                        },
                        {
                            'name': ProjectInitOptions.CONFIG_FILE,
                        },
                        {
                            'name': ProjectInitOptions.ADMIN_USER,
                        },
                        {
                            'name': ProjectInitOptions.CUSTOM_ROUTES,
                        },
                        {
                            'name': ProjectInitOptions.EXAMPLE_PROCESS,
                        },
                        Separator('= DB ='),
                        {
                            'name': ProjectInitOptions.DB_CREATION,
                        },
                    ]
                }
            ])
            if ProjectInitOptions.BASE_PROJECT in responses['todo']:
                # Create base process folder
                if not os.path.exists('./processes'):
                    print('Creating the processes folder..')
                    os.mkdir('processes')
                if not os.path.exists(os.path.join('processes', '__init__.py')):
                    with open(os.path.join('processes', '__init__.py'), 'w') as f:
                        f.write(AppFiles.emptyInit)
                if ProjectInitOptions.EXAMPLE_PROCESS in responses['todo']:
                    if not os.path.exists(os.path.join('processes', 'example_process')):
                        print('Creating example process')

            if ProjectInitOptions.CONFIG_FILE in responses['todo']:
                config_responses = prompt([
                    {
                        'type': 'input',
                        'name': 'host',
                        'message': 'Please enter the webapp host:',
                        'default': 'localhost'
                    },
                    {
                        'type': 'input',
                        'name': 'port',
                        'message': 'Please enter the webapp port:',
                        'default': "5000",
                        'validate': NumberValidator
                    },
                    {
                        'type': 'confirm',
                        'name': 'debug',
                        'message': 'Activate debug mode?',
                        'default': True,
                    },
                    {
                        'type': 'confirm',
                        'name': 'DB',
                        'message': 'Add DB config?',
                        'default': True,
                    },
                ])
                if config_responses['DB']:
                    config_responses['DB'] = prompt([
                        {
                            'type': 'rawlist',
                            'name': 'type',
                            'message': 'Select the database type',
                            'default': DbTypes.SQLLITE,
                            'choices': DbTypes.values()

                        }]
                    )
                    db_questions = {
                        DbTypes.AWS.value: [{
                            'type': 'rawlist',
                            'name': 'type',
                            'message': 'Select the database engine:',
                            'choices': DBEngines.values()

                        }, {
                            'type': 'input',
                            'name': 'user',
                            'default': 'root',
                            'message': 'Enter the root username:',
                        }, {
                            'type': 'password',
                            'name': 'pwd',
                            'message': 'Enter root password:',
                        }, {
                            'type': 'input',
                            'name': 'uri',
                            'message': 'Enter the Db connection url:',
                        }, {
                            'type': 'input',
                            'name': 'instance',
                            'message': 'Enter the Db instance name:',
                        }, {
                            'type': 'input',
                            'name': 'dbname',
                            'message': 'Enter the Db name:',
                        }],
                        DbTypes.SQLLITE.value: [{
                            'type': 'input',
                            'name': 'dbname',
                            'message': 'Enter the Db name:',
                        }]
                    }[config_responses['DB']['type']]
                    config_responses['DB'].update(prompt(db_questions))
                from pprint import pprint
                pprint(config_responses)
                with open('config.yml', 'w') as config_file:
                    yaml.dump(config_responses, config_file, default_flow_style=False)

                # Create extra routes
                custom_extra = AppFiles.custom if ProjectInitOptions.CUSTOM_ROUTES in responses['todo'] else ('', '')

                with open('run.py', 'w') as f:
                    f.write(AppFiles.run % custom_extra)


class DbController(CommanlineController):
    """Controller for the installation-specific tasks:
    - init the db
    - upgrade, migrate, downgrade the db
    """
    callable_cls = True
    command = 'db'

    def init(self):
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

    def upgrade(self):
        try:
            api.upgrade(self.app.config.db_uri, self.app.config.db_repo)
            v = api.db_version(self.app.config.db_uri, self.app.config.db_repo)
        except:
            print(f'{CRED}ERROR!{CEND} Unable to upgrade the database schema.')
            print(traceback.format_exc())
        else:
            print('Done. Current database version: ' + str(v))

    def migrate(self):
        try:
            import imp
            v = api.db_version(self.app.config.db_uri, self.app.config.db_repo)
            migration = f'{self.app.config.db_repo}/versions/{v+1:02}_migration.py'
            tmp_module = imp.new_module('old_model')
            old_model = api.create_model(self.app.config.db_uri, self.app.config.db_repo)
            exec(old_model, tmp_module.__dict__)
            script = api.make_update_script_for_model(self.app.config.db_uri,
                                                      self.app.config.db_repo,
                                                      tmp_module.meta,
                                                      self.app.db.metadata)
            open(migration, "wt").write(script)
            api.upgrade(self.app.config.db_uri, self.app.config.db_repo)
            v = api.db_version(self.app.config.db_uri, self.app.config.db_repo)
        except:
            print(f'{CRED}ERROR!{CEND} Unable to migrate the database schema.')
            print(traceback.format_exc())
        else:
            print('New migration saved as ' + migration)
            print('Current database version: ' + str(v))

    def downgrade(self):
        try:
            v = api.db_version(self.app.config.db_uri, self.app.config.db_repo)
            api.downgrade(self.app.config.db_uri, self.app.config.db_repo, v - 1)
            v = api.db_version(self.app.config.db_uri, self.app.config.db_repo)
        except:
            print(f'{CRED}ERROR!{CEND} Unable to downgrade the database schema.')
            print(traceback.format_exc())
        else:
            print('Done. Current database version: ' + str(v))
