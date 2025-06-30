from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import sqlite3
from datetime import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages

# ─── Email Configuration ──────────────────────────────────────────────
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@gmail.com'          # ← your sender email
EMAIL_PASSWORD = 'your-app-password'            # ← use an app password

def send_email(subject, content, recipient):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg.set_content(content)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"❌ Email failed to send: {e}")

# ─── Database Initialization ─────────────────────────────────────────
def init_db():
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                room_type TEXT NOT NULL,
                checkin TEXT NOT NULL,
                checkout TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
        ''')
        conn.commit()

# ─── Routes ──────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        country_code = request.form.get('country_code', '').strip()
        phone = request.form.get('phone', '').strip()
        room_type = request.form.get('room_type', '').strip()
        checkin = request.form.get('checkin', '').strip()
        checkout = request.form.get('checkout', '').strip()

        full_phone = f"{country_code}{phone}"

        if not all([name, email, phone, country_code, room_type, checkin, checkout]):
            flash("All fields are required.", "error")
            return redirect(url_for('booking'))

        if not phone.isdigit() or not (7 <= len(phone) <= 15):
            flash("Invalid phone number.", "error")
            return redirect(url_for('booking'))

        with sqlite3.connect('kasvi.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (name, email, phone, room_type, checkin, checkout)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, full_phone, room_type, checkin, checkout))
            conn.commit()

        flash("Your booking has been submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('booking.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    errors = {}
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not name:
            errors['name'] = 'Name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not message:
            errors['message'] = 'Message cannot be empty.'

        if errors:
            flash("Please fix the errors below.", "error")
            return render_template('contact.html', errors=errors)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect('kasvi.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (name, email, message, submitted_at)
                VALUES (?, ?, ?, ?)
            ''', (name, email, message, timestamp))
            conn.commit()

        # Send confirmation email to sender
        subject = f"Thank you for contacting Kasvi Palace, {name}!"
        body = f"Dear {name},\n\nThank you for reaching out. We’ve received your message and will get back to you soon.\n\nYour message:\n{message}\n\nRegards,\nKasvi Palace Team"
        send_email(subject, body, email)

        # Optional: Notify admin
        admin_subject = f"New Contact Message from {name}"
        admin_body = f"From: {name} <{email}>\n\n{message}"
        send_email(admin_subject, admin_body, EMAIL_ADDRESS)

        flash("Your message has been sent!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html', errors={})

@app.route('/admin')
def admin():
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings ORDER BY checkin ASC')
        bookings = cursor.fetchall()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin/messages')
def admin_messages():
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY submitted_at DESC')
        messages = cursor.fetchall()
    return render_template('admin_messages.html', messages=messages)

@app.route('/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
    flash('Booking deleted successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
