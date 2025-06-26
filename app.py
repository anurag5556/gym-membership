from flask import Flask, render_template, request, redirect
import psycopg2
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

app = Flask(__name__)

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create table if it doesn't exist
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            phone TEXT,
            joining_date TEXT,
            subscription_type TEXT,
            subscription_duration INTEGER
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, subscription_type, joining_date, subscription_duration FROM subscribers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    members = []

    for row in rows:
        member_id, name, phone, sub_type, join_str, duration = row
        join_date = datetime.strptime(join_str, "%Y-%m-%d")
        end_date = join_date + timedelta(days=duration)
        days_left = (end_date.date() - datetime.today().date()).days
        join_formatted = join_date.strftime('%d/%m/%Y')

        members.append({
            'id': member_id,
            'name': name,
            'phone': phone,
            'type': sub_type,
            'join_date': join_formatted,
            'days_left': days_left
        })

    # Sort so expired members appear at the top
    members.sort(key=lambda x: x['days_left'])

    return render_template("index.html", members=members)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    joining_date_str = request.form['joining_date']  # Format: dd/mm/yyyy
    subscription_type = request.form['subscription_type']
    duration = int(request.form['subscription_duration'])

    # Convert to YYYY-MM-DD for database
    join_date = datetime.strptime(joining_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscribers (name, phone, joining_date, subscription_type, subscription_duration)
        VALUES (%s, %s, %s, %s, %s)
    ''', (name, phone, join_date, subscription_type, duration))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')

@app.route('/renew/<int:id>', methods=['POST'])
def renew(id):
    additional_days = int(request.form['additional_days'])

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_duration FROM subscribers WHERE id = %s", (id,))
    current_duration = cursor.fetchone()

    if current_duration:
        new_duration = current_duration[0] + additional_days
        cursor.execute("UPDATE subscribers SET subscription_duration = %s WHERE id = %s", (new_duration, id))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
