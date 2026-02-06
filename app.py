from flask import Flask, render_template, request, redirect, url_for, session, flash
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for sessions and flash messages

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Login attempt for {username}", "info")
        return redirect(url_for('books'))
    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Registered {username}", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Books listing
@app.route('/books')
def books():
    with open('data/books.json') as f:
        books_data = json.load(f)
    return render_template('books.html', books=books_data)

# Cart page
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

@app.route('/update_cart/<int:book_id>/<action>')
def update_cart(book_id, action):
    cart = session.get('cart', [])

    with open('data/books.json') as f:
        books_data = json.load(f)

    book = next((b for b in books_data if b['id'] == book_id), None)

    if action == 'add' and book:
        cart.append(book)
        flash(f"{book['title']} added to cart!", "success")
    elif action == 'remove':
        cart = [item for item in cart if item['id'] != book_id]
        flash(f"Book {book_id} removed from cart!", "info")

    session['cart'] = cart
    return redirect(url_for('cart'))

# Checkout page
@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] for item in cart_items)
    customer_info = {"name": "Test User", "email": "test@example.com", "address": "123 Street", "payment_method": "Cash on Delivery"}
    return render_template('checkout.html', customer=customer_info, cart=cart_items, total=total_amount)

if __name__ == '__main__':
    app.run(debug=True)

