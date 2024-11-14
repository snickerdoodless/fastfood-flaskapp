# main app file
from flask import Flask, render_template, redirect, url_for
from extensions import mysql, bcrypt
from routes.auth import auth
from routes.menu import menu
from routes.dashboard import dashboard
from routes.cart import cart
from routes.reserve import book
from routes.checkout import checkout
import config
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(config.Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

mysql.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(menu)
app.register_blueprint(cart)
app.register_blueprint(book)
app.register_blueprint(checkout)


