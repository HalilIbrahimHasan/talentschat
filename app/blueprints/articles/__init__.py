from flask import Blueprint

bp = Blueprint('articles', __name__, url_prefix='/w/<workspace_slug>/articles')

from app.blueprints.articles import routes


