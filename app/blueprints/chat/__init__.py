from flask import Blueprint

bp = Blueprint('chat', __name__)

from app.blueprints.chat import routes, sockets


