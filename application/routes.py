from flask import Blueprint, render_template



main = Blueprint('main', __name__)




@main.route('/')
def context():
    return render_template('index.html')
