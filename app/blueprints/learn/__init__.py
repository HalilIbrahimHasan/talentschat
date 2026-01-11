"""Learning module blueprint"""
from flask import Blueprint

bp = Blueprint('learn', __name__, url_prefix='/learn')

from app.blueprints.learn import routes


