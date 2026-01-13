from flask import Blueprint

bp = Blueprint('workspaces', __name__)

from app.blueprints.workspaces import routes




