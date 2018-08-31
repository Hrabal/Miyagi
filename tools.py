# -*- coding: utf-8 -*-
import os
from importlib import import_module


def import_miyagi_modules(base_dir: str=None, internal: bool=False):
    """Scans a folder looking for valid Miyagi processes.
    Imports and yields the found modules.
    :relative_path :: is the path relative to the cwd (presumably the project).
    :default :: overrides the elative_path and imports the internal Miyagi processes
    """
    if internal:
        # Override of the import
        base_dir = os.path.join(os.path.dirname(__file__), 'processes')
        pkg = 'Miyagi.processes'
        pk_arg = {}
    else:
        pk_arg = {'package': base_dir.split('/')[-1]}
        pkg = ''
    for p_name in os.listdir(base_dir):
        # For each valid subfolder..
        if os.path.isdir(os.path.join(base_dir, p_name)) and not p_name.startswith('__'):
            # TODO: subfolder structure validation here
            # We import and yield the module
            yield import_module(f'{pkg}.{p_name}', **pk_arg)


class objdict(dict):
    """dict with attribute access"""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)
