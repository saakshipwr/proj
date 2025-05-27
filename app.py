from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

# Initialize Flask
app = Flask(__name__, template_folder=".")
app.secret_key = 'your_secret_key'  # Use a strong random key in production

# Path to SQLite database
DB_PATH = os.path.join(os.getcwd(), 'users.db')

# Get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure table exists on first run
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home route (optional)
@app.route('/')
def home():
    return render_template('index.html')  # Make sure index.html exists

# --- SIGNUP API ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return "Missing fields", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()

    return "Signup successful", 200


# --- LOGIN API ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return "Login successful", 200
    else:
        return "Invalid email or password", 401

# --- PROFILE PAGE ---
@app.route('/profile')
def profile():
    if 'user_id' in session:
        return f"Welcome, {session['username']}!"
    return redirect(url_for('login_page'))

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# Optional: route to load login.html directly from browser (not via fetch)
@app.route('/login-page')
def login_page():
    return render_template('login.html')

# Optional: same for signup.html
@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

# Run server
if __name__ == '__main__':
    init_db()  # Create DB table if not exists
    app.run(debug=True)
