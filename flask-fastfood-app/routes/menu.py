from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from extensions import mysql

menu = Blueprint('menu', __name__)

@menu.before_request
def initialize_cart():
    if 'cart' not in session:
        session['cart'] = []
        
@menu.route('/menu', methods=['GET'])
def product():
    return render_template('menu.html')

@menu.route('/menu/add_to_cart', methods=['POST'])
def add_cart():
    if 'logged_in' in session:
        user_id = session['user_id']
        product_id = request.form.get('product_id')  
        quantity = int(request.form.get('quantity', 1))  
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """, (user_id, product_id, quantity, quantity))

            mysql.connection.commit()  
            flash("Product Added to Cart!", 'item')  
        except Exception as e:
            mysql.connection.rollback()  
            flash("An error occurred while adding the product to the cart.", 'item')  
            print(e)  
        finally:
            cursor.close()  

        return redirect(url_for('menu.product'))  
    else:
        flash("You need to log in to add items to your cart.")
        return redirect(url_for('auth.login'))  