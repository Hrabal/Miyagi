import argparse
from pyfiglet import Figlet

from .miyagi import App

APP = App(config='config.yml')
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

db_parser = subparsers.add_parser('db')
db_subparser = db_parser.add_subparsers()
db_create = db_subparser.add_parser('create')
db_create.set_defaults(func=APP.db.create)

if __name__ == '__main__':
    f = Figlet(font='colossal')
    print(f.renderText('Miyagi'))
    args = parser.parse_args()
    args.func()
