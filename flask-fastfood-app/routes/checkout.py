from flask import Blueprint, render_template, redirect, session, flash, request, url_for, jsonify
from decimal import Decimal
from extensions import mysql
from validators import validate_ewallet, validate_card
from routes.cart import DELIVERY_FEE

checkout = Blueprint('checkout', __name__)

def get_user_addresses(user_id):
    cursor = mysql.connection.cursor()
    query = """
        SELECT * FROM address 
        WHERE user_id = %s
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        return []

    column_names = [desc[0] for desc in cursor.description]
    addresses = dict(zip(column_names, result))
    cursor.close()

    formatted_addresses = []

    if addresses.get('home_street_address'):
        home_address = {
            'type': 'home',
            'name': addresses['home_address_name'],
            'address': {
                'street': addresses['home_street_address'],
                'unit': addresses['home_unit'],
                'city': addresses['home_city'],
                'state': addresses['home_state'],
                'postal_code': addresses['home_postal_code']
            }
        }
        formatted_addresses.append(home_address)
    
    if addresses.get('office_street_address'):
        office_address = {
            'type': 'office',
            'name': addresses['office_address_name'],
            'address': {
                'street': addresses['office_street_address'],
                'unit': addresses['office_unit'],
                'city': addresses['office_city'],
                'state': addresses['office_state'],
                'postal_code': addresses['office_postal_code']
            }
        }
        formatted_addresses.append(office_address)
    
    return formatted_addresses


@checkout.route('/checkout', methods=['GET', 'POST'], strict_slashes=False)
def payment():
    if 'logged_in' not in session:
        flash("Please Log in to Proceed Payment", "checkout")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    order_summary = []
    subtotal = Decimal('0.00')
    
    addresses = get_user_addresses(user_id)
    if not addresses:
        flash("Please Set up Your Delivery Address First", "update")
        return redirect(url_for('dashboard.dashboard_user'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT cart.quantity, products.name, products.price, products.image_url 
        FROM cart
        JOIN products ON cart.product_id = products.product_id
        WHERE cart.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()
    
    for item in cart_items:
        quantity = item[0]
        name = item[1]
        price = Decimal(str(item[2]))  
        img = item[3]
        
        item_total = Decimal(str(quantity)) * price
        subtotal += item_total
        
        order_summary.append({
            'name': name,
            'quantity': quantity,
            'price': float(price),  
            'image_url': img,
            'item_total': float(item_total)  
        })
        
    subtotal = float(subtotal)
    tax = round(subtotal * 0.017, 2)
    total = round(subtotal + tax + DELIVERY_FEE, 2)
    
    session['checkout_totals'] = {
        'subtotal': float(subtotal),
        'tax': float(tax),
        'fee': float(DELIVERY_FEE),
        'total': float(total)
    }
    
    coupon = ""
    if request.method == 'POST':
        code = request.form.get('coupon_code', '').strip()
        coupon = "Coupon Expired / Does Not Work."
        flash(coupon)
            
    cursor.close()
        
    return render_template('checkout.html', order_summary=order_summary, subtotal=subtotal, tax=tax, fee=DELIVERY_FEE, total=total, coupon=coupon, addresses=addresses)

@checkout.route('/checkout/address_details/<address_type>', strict_slashes=False)
def get_address_details(address_type):
    if 'logged_in' not in session:
        flash("Please Log in to Proceed Payment", "checkout")
        return redirect(url_for('auth.login'))

    if address_type not in ['home', 'office']:
        flash("Invalid Address Type", "error")
        return redirect(url_for('checkout.payment'))

    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()

    if address_type == 'home':
        fields = ['home_street_address', 'home_unit', 'home_city', 
                 'home_state', 'home_postal_code']
    else:
        fields = ['office_street_address', 'office_unit', 'office_city', 
                 'office_state', 'office_postal_code']

    query = f"SELECT {', '.join(fields)} FROM address WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        flash("Address not Found")
        return redirect(url_for('checkout.payment'))

    address = dict(zip(fields, result))

    return jsonify({'address': address})


@checkout.route('/checkout/confirm', methods=['GET','POST'])
def confirm_payment():
    if 'logged_in' not in session:
        flash("Please log in to proceed with payment.", "error")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    totals = session.get('checkout_totals') 
    tax = totals.get('tax', 0.00)  
    payment_method = request.form.get('payment_method')
    ewallet_phone = request.form.get('ewallet_phone')
    ewallet_provider = request.form.get('ewallet_provider')
    card_number = request.form.get('card_number')
    selected_bank = request.form.get('selected_bank')
    
    if payment_method == 'E-Wallet':
        if not ewallet_provider:
            flash("Please select an e-wallet provider.", "error")
            return redirect(url_for('checkout.payment'))
            
        is_valid, error_message = validate_ewallet(ewallet_phone)
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for('checkout.payment'))
            
        payment_details = f"{ewallet_provider} - {ewallet_phone}"
        
    elif payment_method in ['Debit Card', 'Credit Card']:
        if not selected_bank:
            flash("Please select a bank.", "error")
            return redirect(url_for('checkout.payment'))
            
        is_valid, error_message = validate_card(card_number, selected_bank)
        if not is_valid:
            flash(error_message, "error")
            return redirect(url_for('checkout.payment'))
            
        payment_details = f"{selected_bank} Card ending in {card_number[-4:]}"
    
    else:
        flash("Invalid payment method selected.", "error")
        return redirect(url_for('checkout.payment'))

    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT cart.quantity, products.product_id, products.price
            FROM cart
            JOIN products ON cart.product_id = products.product_id
            WHERE cart.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            flash("Your cart is empty.", "error")
            return redirect(url_for('checkout.payment'))

        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, tax, status, payment_method, payment_details)
            VALUES (%s, %s, %s, 'Pending', %s, %s)
        """, (user_id, totals['total'], tax, payment_method, payment_details))
        
        mysql.connection.commit()
        order_id = cursor.lastrowid
        
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item[1], item[0], float(item[2])))
        
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        cursor.close()

        session.pop('checkout_totals', None)
        flash("Payment successful! Your order has been placed.", "success")
        return redirect(url_for('checkout.order_confirmed', order_id=order_id))

    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        flash("An error occurred while processing your payment. Please try again.", "error")
        return redirect(url_for('checkout.payment'))

    

@checkout.route('/checkout/success/<int:order_id>', methods=['GET'], strict_slashes=False)
def order_confirmed(order_id):
    if 'logged_in' not in session:
        flash("Please Log in to View Your Order!")
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT order_id FROM orders WHERE user_id = %s AND order_id = %s", (user_id, order_id))
    order = cursor.fetchone()
    cursor.close()
    
    if not order:
        flash("Order not found or you do not have permission to view this order.", "update")
        return redirect(url_for('dashboard.dashboard_user'))

    return render_template('success.html', order_id=order_id)
