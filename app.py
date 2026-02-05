from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from boto3.dynamodb.conditions import Key
import botocore.exceptions

app = Flask(__name__)
app.secret_key = "your_secret_key"

# --- AWS Resources ---
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Tables (must exist in DynamoDB)
books_table = dynamodb.Table('Books')
cart_table = dynamodb.Table('Cart')
checkout_table = dynamodb.Table('Checkout')

# SNS (must exist in AWS)
sns = boto3.client('sns', region_name='us-east-1')
sns_topic_arn = ""  # replace with your ARN

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Login attempt for {username}", "info")
        return redirect(url_for('books'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Registered {username}", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/books')
def books():
    try:
        response = books_table.scan()
        books_data = response.get('Items', [])
    except botocore.exceptions.ClientError as e:
        flash("Error fetching books from DynamoDB", "danger")
        books_data = []
    return render_template('books.html', books=books_data)

@app.route('/cart')
def cart():
    try:
        response = cart_table.query(
            KeyConditionExpression=Key('user_id').eq('demo_user')
        )
        cart_items = response.get('Items', [])
    except botocore.exceptions.ClientError as e:
        flash("Error fetching cart items", "danger")
        cart_items = []
    return render_template('cart.html', cart=cart_items)

@app.route('/update_cart/<book_id>/<action>')
def update_cart(book_id, action):
    try:
        if action == 'add':
            cart_table.put_item(
                Item={'user_id': 'demo_user', 'book_id': book_id, 'quantity': 1}
            )
            flash("Book added to cart!", "success")
        elif action == 'remove':
            cart_table.delete_item(
                Key={'user_id': 'demo_user', 'book_id': book_id}
            )
            flash("Book removed from cart!", "info")
    except botocore.exceptions.ClientError as e:
        flash("Error updating cart", "danger")
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    order_id = "order123"
    try:
        checkout_table.put_item(
            Item={'order_id': order_id, 'user_id': 'demo_user', 'status': 'Processing'}
        )
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=f"New order placed: {order_id}",
            Subject="BookBazaar Order"
        )
        message = "Order placed successfully!"
    except botocore.exceptions.ClientError as e:
        message = "Error placing order"
    return render_template('checkout.html', message=message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
