from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from boto3.dynamodb.conditions import Key

app = Flask(__name__)
app.secret_key = "your_secret_key"

# AWS resources
dynamodb = boto3.resource('dynamodb')
books_table = dynamodb.Table('Books')
cart_table = dynamodb.Table('Cart')
checkout_table = dynamodb.Table('Checkout')

sns = boto3.client('sns')
sns_topic_arn = "arn:aws:sns:region:account-id:OrderNotifications"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Login attempt for {username}", "info")
        return redirect(url_for('books'))
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        flash(f"Registered {username}", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/books')
def books():
    response = books_table.scan()
    books_data = response['Items']
    return render_template('books.html', books=books_data)

@app.route('/cart')
def cart():
    response = cart_table.query(
        KeyConditionExpression=Key('user_id').eq('demo_user')
    )
    cart_items = response['Items']
    return render_template('cart.html', cart=cart_items)

@app.route('/update_cart/<book_id>/<action>')
def update_cart(book_id, action):
    if action == 'add':
        cart_table.put_item(
            Item={'user_id':'demo_user','book_id':book_id,'quantity':1}
        )
        flash("Book added to cart!", "success")
    elif action == 'remove':
        cart_table.delete_item(
            Key={'user_id':'demo_user','book_id':book_id}
        )
        flash("Book removed from cart!", "info")
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    order_id = "order123"
    checkout_table.put_item(
        Item={'order_id':order_id,'user_id':'demo_user','status':'Processing'}
    )
    sns.publish(
        TopicArn=sns_topic_arn,
        Message=f"New order placed: {order_id}",
        Subject="BookBazaar Order"
    )
    return render_template('checkout.html', message="Order placed successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)