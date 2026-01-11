from flask import Blueprint

bp = Blueprint('api', __name__)

from app.blueprints.api import routes
from app.blueprints.api import learning_routes


