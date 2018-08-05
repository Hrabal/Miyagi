from tempy.tags import Link, Script


class JQuery:
    js = Script(src="https://code.jquery.com/jquery-3.3.1.min.js")


class Bootstrap4:
    css = Link(rel="stylesheet",
               href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
               integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm",
               crossorigin="anonymous")
    js = Script(src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js",
                integrity="sha384-alpBpkh1PFOepccYVYDB4do5UnbKysX5WZXm3XxPqe5iKTfUKjNkCk9SaVuEZflJ",
                crossorigin="anonymous")


class FontAwesome:
    css = Link(rel="stylesheet",
               href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",
               integrity="sha384-hWVjflwFxL6sNzntih27bfxkr27PmbbK/iSvJ+a4+0owXq79v+lsFkW54bOGbiDQ",
               crossorigin="anonymous")
    js = Script(defer=True, src="https://use.fontawesome.com/releases/v5.2.0/js/all.js",
                integrity="sha384-4oV5EgaV02iISL2ban6c/RmotsABqE4yZxZLcYMAdG7FAPsyHYAPpywE9PJo+Khy",
                crossorigin="anonymous")


class MainCSS:
    css = Link(rel="stylesheet", href="/static/base/css/dashboard.css")


class Popper:
    js = Script(src='https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js')
