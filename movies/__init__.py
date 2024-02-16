from flask import Flask
from movies import pages
from movies.coldstart import bp as coldstart_bp
from movies.filtering import bp as filtering_bp
from movies.hybrid import bp as hybrid_bp

#  python -m flask --app movies run --port 5000 --debug

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    app.register_blueprint(coldstart_bp, url_prefix='/coldstart')
    app.register_blueprint(filtering_bp, url_prefix='/collaborative')
    app.register_blueprint(hybrid_bp, url_prefix='/hybrid')

    return app