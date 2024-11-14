# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql, bcrypt
from validators import validate_email, validate_password, validate_phone

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    if request.method == 'POST':
        user_data = {
            'email': request.form['email'],
            'password': request.form['password'],
            'confirm_password': request.form['confirm_password'],
            'full_name': request.form['full_name'],
            'phone': request.form['phone']
        }

        if user_data:
            validate_email(user_data['email']) 
            validate_password(user_data['password']) 
            validate_phone(user_data['phone'])

        if user_data['password'] != user_data['confirm_password']:
            flash("Passwords do not Match.", "register")
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (user_data['email'],))
        account = cursor.fetchone()

        if account:
            flash("Account Already Exists! Please Log in.", "register")
            return redirect(url_for('auth.login'))

        cursor.execute("""
            INSERT INTO users (email, password, full_name, phone)
            VALUES (%s, %s, %s, %s)
        """, (
            user_data['email'], hashed_password, user_data['full_name'], user_data['phone']
        ))

        mysql.connection.commit()
        cursor.close()

        flash("Registration Successful! Please Log in.", "register")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if 'logged_in' in session:
        session.permanent = True
        return redirect(url_for('dashboard.dashboard_user'))

    elif 'logged_in' not in session and request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[2], password):  
            session.permanent = True
            session['logged_in'] = True
            session['user_id'] = user[0]  
            session['email'] = user[1]   
            flash("Logged in Successfully!", 'user')
            return redirect(url_for('dashboard.dashboard_user'))
        else:
            flash("Invalid email or password.", "login")

    return render_template('login.html')


@auth.route('/logout', methods=['GET'], strict_slashes=False)
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth.before_app_request
def refresh_session_lifetime():
    if 'logged_in' in session:
        session.permanent = True  