from flask import Blueprint

bp = Blueprint('videos', __name__)

from app.blueprints.videos import routes


