import argparse
import inspect

from .commandline import controllers
from .miyagi import App

APP = App(config='config.yml', as_script=True)
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

for _, cls in inspect.getmembers(controllers, inspect.isclass):
    if getattr(cls, '_callable', False):
        cls_parser = subparsers.add_parser(cls._command)
        controller = cls(APP)
        method_parser = cls_parser.add_subparsers()
        for _, fnc in inspect.getmembers(controller, inspect.ismethod):
            if fnc.__name__ != '__init__':
                method = method_parser.add_parser(fnc.__name__)
                method.set_defaults(func=fnc)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func()
