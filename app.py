from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

DB_FILE = 'gym.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            joining_date TEXT,
            subscription_type TEXT,
            subscription_duration INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, subscription_type, joining_date, subscription_duration FROM subscribers")
    rows = cursor.fetchall()
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

    # Sort members: expired ones (days_left < 0) come first
    members.sort(key=lambda x: x['days_left'])

    return render_template("index.html", members=members)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    joining_date_str = request.form['joining_date']  # Format: dd/mm/yyyy
    subscription_type = request.form['subscription_type']
    duration = int(request.form['subscription_duration'])

    # Convert to YYYY-MM-DD for storage
    join_date = datetime.strptime(joining_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscribers (name, phone, joining_date, subscription_type, subscription_duration)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, phone, join_date, subscription_type, duration))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/renew/<int:id>', methods=['POST'])
def renew(id):
    additional_days = int(request.form['additional_days'])

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_duration FROM subscribers WHERE id = ?", (id,))
    current_duration = cursor.fetchone()
    
    if current_duration:
        new_duration = current_duration[0] + additional_days
        cursor.execute("UPDATE subscribers SET subscription_duration = ? WHERE id = ?", (new_duration, id))
        conn.commit()
    
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
