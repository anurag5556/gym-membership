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
    cursor.execute("SELECT name, phone, subscription_type, joining_date, subscription_duration FROM subscribers")
    rows = cursor.fetchall()
    conn.close()

    subscribers = []
    expired = []

    for row in rows:
        name, phone, sub_type, join_str, duration = row
        join_date = datetime.strptime(join_str, "%Y-%m-%d")
        end_date = join_date + timedelta(days=duration)
        days_left = (end_date.date() - datetime.today().date()).days
        join_formatted = join_date.strftime('%d/%m/%Y')

        subscribers.append({
            'name': name,
            'phone': phone,
            'type': sub_type,
            'join_date': join_formatted,
            'days_left': days_left
        })

        if days_left < 0:
            expired.append(name)

    return render_template("index.html", subscribers=subscribers, expired=expired)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    joining_date = request.form['joining_date']  # Format: YYYY-MM-DD
    subscription_type = request.form['subscription_type']
    duration = int(request.form['subscription_duration'])

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscribers (name, phone, joining_date, subscription_type, subscription_duration)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, phone, joining_date, subscription_type, duration))
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
