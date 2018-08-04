from .miyagi import App


class MiyagiRoute:
    def __init__(self, app: App, uri: str, methods: list, fnc):
        self.app = app
        self.uri = uri
        self.methods = methods
        self.fnc = fnc
