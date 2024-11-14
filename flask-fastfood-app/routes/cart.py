from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request, flash
from extensions import mysql

cart = Blueprint('cart', __name__)

DELIVERY_FEE = 5.00

@cart.route('/cart', methods=['GET'], strict_slashes=False)
def view_cart():
    if 'user_id' not in session:
        flash("Please Log in to View Your Cart.")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.name, p.price, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()
    cursor.close()

    cart_data = [
        {
            "id": item[0],
            "quantity": item[1],
            "name": item[2],
            "price": float(item[3]),
            "total_price": float(item[1]) * float(item[3]),
            "image_url": item[4]
        }
        for item in cart_items
    ]
    
    subtotal = sum(item['total_price'] for item in cart_data)
    total = subtotal + DELIVERY_FEE
    item_count = sum(item['quantity'] for item in cart_data) 

    return render_template(
        'cart.html', cart_items=cart_data, subtotal=subtotal, delivery_fee=DELIVERY_FEE, total=total, item_count=item_count
    )

@cart.route('/cart/update_quantity', methods=['POST'], strict_slashes=False)
def update_quantity():
    """Update quantity of a specific item in the cart."""
    if 'user_id' not in session:
        return jsonify({"error": "Please log in to update your cart."}), 401

    user_id = session['user_id']
    product_id = request.json.get('product_id')
    change = request.json.get('change')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    item = cursor.fetchone()

    if item:
        new_quantity = item[0] + change
        if new_quantity <= 0:
            cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        else:
            cursor.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s", (new_quantity, user_id, product_id))
    else:
        if change > 0:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, change))

    mysql.connection.commit()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    updated_cart_items = cursor.fetchall()
    cursor.close()

    updated_cart_data = [
        {
            "id": item[0],
            "quantity": item[1],
            "price": float(item[2]),
            "total_price": float(item[1]) * float(item[2])
        }
        for item in updated_cart_items
    ]
    subtotal = sum(item['total_price'] for item in updated_cart_data)
    total = subtotal + DELIVERY_FEE

    item_total = next((i['total_price'] for i in updated_cart_data if i['id'] == int(product_id)), 0)
    return jsonify({"quantity": new_quantity, "item_total": item_total, "subtotal": subtotal, "total": total})
