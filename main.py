
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# ─── Generate PDF Invoice ───
def generate_invoice(name, email, phone, room_type, checkin, checkout):
    if not os.path.exists('static/invoices'):
        os.makedirs('static/invoices')
    filename = f"invoice_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    path = f"static/invoices/{filename}"

    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Kasvi Palace - Booking Invoice")
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Name: {name}")
    c.drawString(50, 700, f"Email: {email}")
    c.drawString(50, 680, f"Phone: {phone}")
    c.drawString(50, 660, f"Room: {room_type}")
    c.drawString(50, 640, f"Check-in: {checkin}")
    c.drawString(50, 620, f"Check-out: {checkout}")
    c.drawString(50, 600, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, 570, "Thank you for booking with Kasvi Palace!")
    c.save()
    return path

# ─── Initialize Database ───
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurant_menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                guests INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        conn.commit()

# ─── Routes ───
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/restaurant')
def restaurant():
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, category, price, description FROM restaurant_menu ORDER BY category")
        menu = cursor.fetchall()
    return render_template('restaurant.html', menu=menu)

@app.route('/restaurant/book', methods=['POST'])
def book_table():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    guests = request.form['guests']
    date = request.form['date']
    time = request.form['time']

    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO table_bookings (name, email, phone, guests, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, guests, date, time))
        conn.commit()

    flash("Your table has been booked successfully!", "success")
    return redirect(url_for('restaurant'))

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
            booking_id = cursor.lastrowid
            conn.commit()

        generate_invoice(name, email, full_phone, room_type, checkin, checkout)
        flash("Your booking has been submitted successfully!", "success")
        return redirect(url_for('thank_you', booking_id=booking_id))

    return render_template('booking.html')

@app.route('/thankyou')
def thank_you():
    booking_id = request.args.get('booking_id')
    return render_template('thank_you.html', recent_booking_id=booking_id)

@app.route('/invoice/<int:booking_id>')
def generate_invoice_route(booking_id):
    with sqlite3.connect('kasvi.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, phone, room_type, checkin, checkout FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()

    if row:
        name, email, phone, room_type, checkin, checkout = row
        invoice_path = generate_invoice(name, email, phone, room_type, checkin, checkout)
        return send_from_directory('static/invoices', os.path.basename(invoice_path), as_attachment=True)
    else:
        flash("Invoice not found.", "error")
        return redirect(url_for('admin'))

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

        submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect('kasvi.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (name, email, message, submitted_at)
                VALUES (?, ?, ?, ?)
            ''', (name, email, message, submitted_at))
            conn.commit()

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

@app.route('/export/bookings')
def export_bookings():
    with sqlite3.connect('kasvi.db') as conn:
        df = pd.read_sql_query("SELECT * FROM bookings", conn)
        export_path = 'static/exports/bookings.xlsx'
        if not os.path.exists('static/exports'):
            os.makedirs('static/exports')
        df.to_excel(export_path, index=False)
    return send_from_directory('static/exports', 'bookings.xlsx', as_attachment=True)

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
