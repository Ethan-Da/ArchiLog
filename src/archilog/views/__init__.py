
from flask import Flask


def create_app():
    app = Flask(__name__)

    from archilog.views.web import web_ui
    app.register_blueprint(web_ui)
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")




    return app
