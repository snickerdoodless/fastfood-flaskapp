from flask import Blueprint, render_template, redirect, url_for, session, flash, request    
from extensions import mysql

book = Blueprint('book', __name__)

@book.route('/reserve', methods=['GET'])
def booking():
    return render_template('book.html')

@book.route('/reserve/create', methods=['POST'])
def reservations():
    if 'logged_in' not in session:
        flash('Please Login to Make Reservation!', 'book')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        date = request.form.get('reservation_date')
        time = request.form.get('reservation_time')
        guest = request.form.get('number_of_guests')
        note = request.form.get('special_requests', '')
        
        cursor = mysql.connection.cursor()
        cursor.execute(""" INSERT INTO reservations (user_id, reservation_date, reservation_time, number_of_guests, special_requests)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (user_id, date, time, guest, note))
        
        mysql.connection.commit()
        cursor.close()
        
        flash("Reservations Has Been Made. Please Wait for Email!", 'book')
        return redirect(url_for('book.booking'))

