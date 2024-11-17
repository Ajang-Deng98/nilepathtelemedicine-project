from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Appointment  # Assuming these models are defined in 'models.py'
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

import os
from dotenv import load_dotenv

import requests

load_dotenv()

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ajangcholaguer98@gmail.com'
app.config['MAIL_PASSWORD'] = 'guij aytb xayu qwmt'
app.config['MAIL_DEFAULT_SENDER'] = 'ajangcholaguer98@gmail.com'

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)  # Token serializer for reset links
db.init_app(app)

serializer = URLSafeTimedSerializer(app.secret_key)

# Create tables before the first request
@app.before_request
def create_tables():
    if not hasattr(create_tables, 'has_run'):
        db.create_all()
        create_tables.has_run = True

# Index Route (Home Page)
@app.route('/')
def index():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please use a different email or log in.', 'danger')
            return redirect(url_for('register'))
        
        name = request.form['name']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        county = request.form['county']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        new_user = User(name=name, email=email, dob=dob, county=county, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in to continue.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    
    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    return render_template('dashboard.html', user=user)

# Clinic Finder Route
@app.route('/clinic_finder')
def clinic_finder():
    if 'user_id' not in session:
        flash('Please log in to find clinics.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('clinic-finder.html')

# Disease Information Route
@app.route('/disease_info')
def disease_info():
    
    return render_template('disease-info.html')

# Book Appointment Route
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    return render_template('book-appointment.html')




@app.route('/result')
def result():
    return render_template('result.html')

# Route for Health Guides
@app.route('/health-guides')
def health_guides():
    # You can replace this with your actual content
    return render_template('health_guides.html')

# Route for Medication Information
@app.route('/medication-info')
def medication_info():
    # You can replace this with your actual content
    return render_template('medication_info.html')

# Route for Health Articles
@app.route('/health-articles')
def health_articles():
    # You can replace this with your actual content
    return render_template('health_articles.html')



# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            # Here, send the `reset_url` to the user via email
            msg = Message("Password Reset Request", sender="your-email@example.com", recipients=[email])
            msg.body = f"To reset your password, click the link: {reset_url}"
            mail.send(msg)

        flash('If an account with that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')


# Reset Password Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # Verify the token
    except SignatureExpired:
        flash('The reset link has expired.', 'danger')
        return redirect(url_for('forgot_password'))
    except Exception:
        flash('The reset link is invalid.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)






# Define the API endpoint and headers for RapidAPI
RAPIDAPI_URL = "https://bmi.p.rapidapi.com/v1/bmi"
RAPIDAPI_HEADERS = {
    'x-rapidapi-key': "1e30b9b14dmshc7fd4d8abafd6b9p1a2636jsn8261b0d5abfb",
    'x-rapidapi-host': "bmi.p.rapidapi.com",
    'Content-Type': "application/json"
}

@app.route("/bmi_checker")
def bmi_checker():
    return render_template("bmi_checker.html")

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    # Collect data from the form
    weight = request.form['weight']
    height = request.form['height']
    age = request.form['age']
    sex = request.form['sex']
    

    # Construct the payload for the API request
    payload = {
        "weight": {"value": weight, "unit": "kg"},
        "height": {"value": height, "unit": "cm"},
        "sex": sex,
        "age": age,
        
    }

    # Make the API request to RapidAPI
    response = requests.post(RAPIDAPI_URL, headers=RAPIDAPI_HEADERS, json=payload)

    # Handle the response from the API
    if response.status_code == 200:
        bmi_data = response.json()
        bmi_value = bmi_data.get("bmi", "Not available")
        bmi_category = bmi_data.get("bmi_category", "Not available")
        health_risk = bmi_data.get("health_risk", "Not available")

        # Render the result on a new page
        return render_template('result.html', bmi=bmi_value, category=bmi_category, risk=health_risk)
    else:
        return f"Error: {response.status_code} - {response.text}"

























# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ajangcholaguer98@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'guij aytb xayu qwmt'  # Your generated app password
app.config['MAIL_DEFAULT_SENDER'] = 'ajangcholaguer98@gmail.com'

mail = Mail(app)

# Dictionary mapping doctor names to their respective email addresses
DOCTORS_EMAILS = {
    'Dr. Smith': 'a.deng3@alustudent.com',
    'Dr. John': 'ajangdeng1000@gmail.com',
    'Dr. Williams': 'malokajith5@gmail.com',
    'Dr. Timothy': 'bulajak196@gmail.com',
    'Dr. Aaron': 'dengajang1516@gmail.com'
}

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')        # New: User's name
    age = data.get('age')          # New: User's age
    doctor = data.get('doctor')    # Get the selected doctor's name
    user_email = data.get('email') # Get the user's email
    location = data.get('location')
    date = data.get('date')
    time = data.get('time')
    booking_details = data.get('details')

    # Get the email of the selected doctor
    doctor_email = DOCTORS_EMAILS.get(doctor)

    if not doctor_email:
        return jsonify({"success": False, "message": "Invalid doctor selected"}), 400

    # Create the email message to send to the doctor
    msg_to_doctor = Message(
        subject="New Appointment Booking",
        recipients=[doctor_email],  # Send the email to the doctor's email
        body=(
            f"New appointment booking from {name} (Age: {age}).\n\n"
            f"Email: {user_email}\n"
            f"Details: {booking_details}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Location: {location}\n"
        )
    )

    # Create the email message to send to the app's email
    msg_to_app = Message(
        subject="New Appointment Booking Copy",
        recipients=[app.config['MAIL_USERNAME']],  # Send the email to the app's email
        body=(
            f"New appointment booking from {name} (Age: {age}).\n\n"
            f"Email: {user_email}\n"
            f"Details: {booking_details}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Location: {location}\n"
        )
    )

    # Create the email message to send to the user's email
    msg_to_user = Message(
        subject="Your Appointment Booking Confirmation",
        recipients=[user_email],  # Send the email to the user's email
        body=(
            f"Thank you for booking an appointment, {name}.\n\n"
            f"Details:\n"
            f"Doctor: {doctor}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Location: {location}\n"
            f"Additional Details: {booking_details}\n\n"
            "Please keep this confirmation for your records."
        )
    )

    try:
        # Send email to the selected doctor
        mail.send(msg_to_doctor)
        # Send a copy to the app's email
        mail.send(msg_to_app)
        # Send a copy to the user's email
        mail.send(msg_to_user)
        return jsonify({"success": True, "message": "Emails sent to doctor, app, and user successfully"}), 200
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return jsonify({"success": False, "message": "Failed to send email"}), 500
    
    

if __name__ == '__main__':
    app.run(debug=True)
