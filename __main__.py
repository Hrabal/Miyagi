#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import argparse
import inspect

from .commandline import controllers
from .miyagi import App

# Instantiate an App object so every commandline controller have access to the
# installation-specific configs, dbs, etc.
APP = App(config='config.yml')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# For every controller class defined in the commandline.controllers module we add a subparser
for _, cls in inspect.getmembers(controllers, inspect.isclass):
    # Only classes with _callable will be added as subparser (so to exclude utility classes)
    if getattr(cls, '_callable', False):
        # Bind the subparser to the _command defined in the class
        cls_parser = subparsers.add_parser(cls._command)
        # Instantiate the controller class
        controller = cls(APP)
        # Every method in the controller class will have it's own subparser
        method_parser = cls_parser.add_subparsers()
        for _, fnc in inspect.getmembers(controller, inspect.ismethod):
            if fnc.__name__ != '__init__':
                method = method_parser.add_parser(fnc.__name__)
                # Bind the class method to the subparser argument
                method.set_defaults(func=fnc)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func()
