from flask import Flask


def create_app():
    app = Flask(__name__)

    from archilog.views.web import web_ui
    from archilog.views.api import api
    from archilog.views.api import spec
    app.register_blueprint(web_ui)
    app.register_blueprint(api)
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")

    spec.register(app)

    return app
