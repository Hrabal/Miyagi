
class MiyagiRoute:
    def __init__(self, uri: str, methods: list, fnc):
        self.uri = uri
        self.methods = methods
        self.handler = fnc
