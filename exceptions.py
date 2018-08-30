# -*- coding: utf-8 -*-


class MiyagiError(Exception): pass


class InitError(MiyagiError): pass


class MiyagiTypeError(InitError, TypeError):
    def __init__(self, *args, **kwargs):
        self.obj = kwargs.pop('obj', None)
        self.par = kwargs.pop('par', None)
        self.expected = kwargs.pop('expected', '')
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'\n\nInvalid object for parameter {self.par}: "{self.obj}".\nGot {self.obj.__class__} expected {self.expected or "<undefined>"}'
