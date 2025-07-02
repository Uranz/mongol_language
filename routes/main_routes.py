from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html') 