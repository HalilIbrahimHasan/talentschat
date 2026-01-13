from flask import Blueprint

bp = Blueprint('channels', __name__)

from app.blueprints.channels import routes




