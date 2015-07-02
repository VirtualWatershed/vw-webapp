from flask import Blueprint

visualization = Blueprint('visualization', __name__)

from . import views
