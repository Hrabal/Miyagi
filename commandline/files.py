
class AppFiles:
    run = """
from Miyagi import App

%s

if __name__ == "__main__":
    app = App(config='config.yml'%s)
    app.run()

"""
    custom_extra = ("from app import custom", ", blueprints=[custom, ]")
    custom_app = """
from vibora.blueprints import Blueprint
from vibora.responses import JsonResponse

from Miyagi.config import Config

frontend = Blueprint()


@frontend.route("/custom_route", methods=['GET'])
async def home(config: Config):
    return JsonResponse({'foo': 'bar'})

"""
