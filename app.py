from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from web3 import Web3
from mpesa_utils import lipa_na_mpesa_online  # Import the function
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Retrieve MPESA credentials from environment variables
consumer_key = os.getenv('MPESA_CONSUMER_KEY')
consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
shortcode = os.getenv('MPESA_SHORTCODE')
passkey = os.getenv('MPESA_PASSKEY')
callback_url = os.getenv('MPESA_CALLBACK_URL')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Connect to local Ganache instance
ganache_url = 'http://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Dummy package data (if needed, can be replaced by database entries)
packages = [
    {"id": 1, "name": "1hr @ 20bob (2mbps)", "description": "1 hour of internet at 2mbps", "price": 20},
    {"id": 2, "name": "8hrs @ 50bob (2mbps)", "description": "8 hours of internet at 2mbps", "price": 50},
    {"id": 3, "name": "24hrs @ 80bob (2mbps)", "description": "24 hours of internet at 2mbps", "price": 80},
    {"id": 4, "name": "1 device @ 250 (2mbps)", "description": "1 week for 1 device at 2mbps", "price": 250},
    {"id": 5, "name": "3 devices @ 350 (2mbps)", "description": "1 week for 3 devices at 2mbps", "price": 350},
    {"id": 6, "name": "2mbps @ 1000", "description": "1 month at 2mbps", "price": 1000},
    {"id": 7, "name": "4mbps @ 1500", "description": "1 month at 4mbps", "price": 1500},
    {"id": 8, "name": "6mbps @ 2000", "description": "1 month at 6mbps", "price": 2000},
    {"id": 9, "name": "8mbps @ 2500", "description": "1 month at 8mbps", "price": 2500},
    {"id": 10, "name": "10mbps @ 3000", "description": "1 month at 10mbps", "price": 3000}
]

# Define your models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    othername = db.Column(db.String(80), nullable=True)
    contact = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Package {self.name}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    subscription_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    package = db.relationship('Package', backref=db.backref('subscriptions', lazy=True))

    def __repr__(self):
        return f'<Subscription UserID: {self.user_id}, PackageID: {self.package_id}>'

# Define your routes
@app.route('/')
def home():
    return redirect(url_for('default_page'))

@app.route('/default')
def default_page():
    return render_template('default.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        surname = request.form['surname']
        firstname = request.form['firstname']
        othername = request.form['othername']
        contact = request.form['contact']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user = User(
            username=username,
            email=email,
            surname=surname,
            firstname=firstname,
            othername=othername,
            contact=contact,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('view_packages'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Simulate sending a password reset email
            flash(f'Password reset instructions have been sent to {email}.', 'success')
        else:
            flash('Email not found in our records.', 'error')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/packages')
def view_packages():
    if 'user_id' not in session:
        flash('Please log in to view packages.', 'warning')
        return redirect(url_for('login'))
    
    packages = Package.query.all()
    return render_template('packages.html', packages=packages)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.surname = request.form['surname']
        user.firstname = request.form['firstname']
        user.othername = request.form['othername']
        user.contact = request.form['contact']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    
    return render_template('profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please log in to change your password.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        new_password = request.form['new_password']
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')

@app.route('/subscribe/<int:package_id>', methods=['POST'])
def subscribe(package_id):
    if 'user_id' not in session:
        flash('Please log in to subscribe.', 'warning')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    subscription = Subscription(user_id=user_id, package_id=package_id)
    db.session.add(subscription)
    db.session.commit()
    flash('Subscription successful!', 'success')
    
    # Redirect to a payment page (dummy link or an actual payment processing page)
    return redirect(url_for('payment', package_id=package_id))

@app.route('/payment/<int:package_id>')
def payment(package_id):
    package = db.session.get(Package, package_id)  # New method using db.session.get()
    return render_template('payment.html', package=package)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Please log in to make a payment.', 'warning')
        return redirect(url_for('login'))
    
    package_id = request.form.get('package_id')
    mpesa_number = request.form.get('mpesa_number')

    if not package_id or not mpesa_number:
        flash('Invalid payment details. Please try again.', 'danger')
        return redirect(url_for('view_packages'))

    try:
        package_id = int(package_id)  # Ensure package_id is an integer
    except ValueError:
        flash('Invalid package ID. Please try again.', 'danger')
        return redirect(url_for('view_packages'))

    package = Package.query.get(package_id)
    if not package:
        flash('Package not found.', 'danger')
        return redirect(url_for('view_packages'))

    # Retrieve MPESA credentials from environment variables
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    shortcode = os.getenv('MPESA_SHORTCODE')
    passkey = os.getenv('MPESA_PASSKEY')
    callback_url = os.getenv('MPESA_CALLBACK_URL')

    # Initiate MPESA payment
    payment_response = lipa_na_mpesa_online(
        mpesa_number,
        package.price,
        str(package_id),
        consumer_key,
        consumer_secret,
        shortcode,
        passkey,
        callback_url
    )

    if payment_response.get('ResponseCode') == '0':
        flash('Payment request sent successfully! Please complete the payment on your phone.', 'success')
    else:
        flash('Payment failed. Please try again.', 'danger')

    # Redirect to a success page or back to packages
    return redirect(url_for('view_packages'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

