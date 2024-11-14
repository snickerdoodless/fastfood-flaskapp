from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from extensions import mysql
from datetime import datetime, timedelta
from routes.cart import DELIVERY_FEE

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard', methods=['GET'], strict_slashes=False)
def dashboard_user():
    if 'logged_in' in session:
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT full_name, email, phone FROM users WHERE user_id = %s", (session['user_id'],))
        user_info = cursor.fetchone()
        
        if not user_info:
            user_info = ("", "", "")
        
        cursor.execute("""
            SELECT home_street_address, home_unit, home_city, home_state, home_postal_code,
                   office_street_address, office_unit, office_city, office_state, office_postal_code
            FROM address WHERE user_id = %s
        """, (session['user_id'],))
        
        address_info = cursor.fetchone()
        cursor.close()

        if not address_info:
            address_info = [""] * 10  

        home_address = {
            "street": address_info[0],
            "unit": address_info[1],
            "city": address_info[2],
            "state": address_info[3],
            "postal_code": address_info[4]
        }
        
        office_address = {
            "street": address_info[5],
            "unit": address_info[6],
            "city": address_info[7],
            "state": address_info[8],
            "postal_code": address_info[9]
        }

        return render_template('profile.html', user_data=user_info, home_address=home_address, office_address=office_address)

    else:
        flash("Please Log in to Access the Dashboard!")
        return redirect(url_for('auth.login'))


@dashboard.route('/update_address', methods=['POST'])
def update_address():
    if 'logged_in' not in session:
        flash("Please Log in to Access Dashboard!")
        return redirect(url_for('auth.login'))
    
    address_type = request.form.get('address_type')

    data = {
        f"{address_type}_street_address": request.form.get('street'),
        f"{address_type}_unit": request.form.get('unit'),
        f"{address_type}_city": request.form.get('city'),
        f"{address_type}_state": request.form.get('state'),
        f"{address_type}_postal_code": request.form.get('zip'),
    }

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM address WHERE user_id = %s", (session['user_id'],))
    existing_address = cursor.fetchone()

    if address_type == "home":
        if existing_address:
            cursor.execute("""
                UPDATE address SET 
                    home_street_address = %s, 
                    home_unit = %s, 
                    home_city = %s, 
                    home_state = %s, 
                    home_postal_code = %s
                WHERE user_id = %s
            """, (
                data['home_street_address'], 
                data['home_unit'], 
                data['home_city'], 
                data['home_state'], 
                data['home_postal_code'], 
                session['user_id']
            ))

            address_label = "Home Address"
        else:
            cursor.execute("""
                INSERT INTO address (user_id, home_street_address, home_unit, home_city, home_state, home_postal_code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['user_id'], 
                data['home_street_address'], 
                data['home_unit'], 
                data['home_city'], 
                data['home_state'], 
                data['home_postal_code']
            ))
            address_label = "New Home Address"

    elif address_type == "office":
        fields_to_update = {k: v for k, v in data.items() if v and k.startswith("office")}

        if fields_to_update:
            if existing_address:
                update_query = ", ".join([f"{key} = %s" for key in fields_to_update.keys()])
                values = list(fields_to_update.values()) + [session['user_id']]
                cursor.execute(f"UPDATE address SET {update_query} WHERE user_id = %s", values)
                address_label = "Office Address"
            else:
                cursor.execute("""
                    INSERT INTO address (user_id, office_street_address, office_unit, office_city, office_state, office_postal_code)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    session['user_id'], 
                    data.get('office_street_address'), 
                    data.get('office_unit'), 
                    data.get('office_city'), 
                    data.get('office_state'), 
                    data.get('office_postal_code')
                ))
                address_label = "New Office Address"
        else:
            flash("No Office Address Fields to Update.", "update")
            return redirect(url_for('dashboard.dashboard_user'))

    else:
        flash("Invalid Address Type!", "update")
        return redirect(url_for('dashboard.dashboard_user'))

    mysql.connection.commit()
    cursor.close()

    flash(f"{address_label} Successfully Updated!", "update")
    return redirect(url_for('dashboard.dashboard_user'))


@dashboard.route('/dashboard/order', methods=['GET'], strict_slashes=False)
def order_history():
    if 'logged_in' not in session:
        flash("Please Log in to Access Dashboard!")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT order_id, total_amount, tax, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    orders = cursor.fetchall()
    
    order_data = []

    for order in orders:
        order_id, total_amount, tax, status, created_at = order

        cursor.execute("""
            SELECT oi.quantity, oi.price, p.name
            FROM order_items AS oi
            JOIN products AS p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        order_items = cursor.fetchall()

        items_list = []
        for item in order_items:
            quantity, price, product_name = item
            items_list.append({
                'product_name': product_name,
                'quantity': quantity,
                'price': price
            })
    
        order_data.append({
            'order_id': order_id,
            'total_amount': total_amount,
            'tax': tax,
            'delivery_fee': DELIVERY_FEE,  
            'status': status,
            'created_at': created_at,
            'order_items': items_list  
        })

    cursor.close()
    
    return render_template('order.html', orders=order_data)


@dashboard.route('/dashboard/reservation', methods=['GET', 'POST'], strict_slashes=False)
def reservations_dashboard():
    if 'logged_in' not in session:
        flash("Please Log in to Access Dashboard!")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT reservation_id, reservation_date, reservation_time, number_of_guests,
               special_requests, status, created_at
        FROM reservations
        WHERE user_id = %s
        ORDER BY reservation_date DESC, reservation_time DESC
    """, (user_id,))
    
    reservations = cursor.fetchall()

    reservation_data = []
    for reservation in reservations:
        reservation_id, reservation_date, reservation_time, num_guests, special_requests, status, created_at = reservation
        
        if isinstance(reservation_date, str):
            reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d')  

        if isinstance(reservation_time, timedelta):
            time_of_day = (datetime.min + reservation_time).time()
            formatted_time = time_of_day
        else:
            formatted_time = reservation_time  

        reservation_data.append({
            'reservation_id': reservation_id,
            'reservation_date': reservation_date,  
            'reservation_time': formatted_time,  
            'number_of_guests': num_guests,
            'special_requests': special_requests,
            'status': status,
            'created_at': created_at
        })

    cursor.close()

    return render_template('reservation.html', reservations=reservation_data)