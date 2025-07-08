# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

auth_bp = Blueprint('auth', __name__, template_folder='templates')

# helper to get DB
def get_db():
    db_path = os.getenv('DB_PATH', 'finances.db')
    return sqlite3.connect(db_path)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        pw    = request.form['password']
        conn = get_db()
        cur = conn.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            flash('Email already registered', 'danger')
        else:
<<<<<<< HEAD
            # create and commit new user
            cur = conn.execute(
                "INSERT INTO users (email,password_hash) VALUES (?,?)",
                (email, generate_password_hash(pw))
            )
            conn.commit()
            user_id = cur.lastrowid
            conn.close()

            # log them in immediately
            user = User(user_id, email)
            login_user(user)

            # redirect to dashboard
            return redirect(url_for('dashboard.dashboard'))

    # on GET or failed POST
=======
            conn.execute(
              "INSERT INTO users (email,password_hash) VALUES (?,?)",
              (email, generate_password_hash(pw))
            )
            conn.commit()
            conn.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
>>>>>>> origin/main
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        pw    = request.form['password']
        conn = get_db()
        row = conn.execute(
          "SELECT id,password_hash FROM users WHERE email=?", (email,)
        ).fetchone()
        conn.close()
        if row and check_password_hash(row[1], pw):
            user = User(row[0], email)       # we'll define User below
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.email == 'guest@demo':
        conn = get_db()
        conn.execute('DELETE FROM tx WHERE user_id = ?', (current_user.id,))
        conn.execute('DELETE FROM users WHERE id = ?', (current_user.id,))
        conn.commit()
        conn.close()
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/guest')
def guest():
    # Connect to DB
    conn = get_db()
    # Look for an existing guest account
    row = conn.execute("SELECT id,email FROM users WHERE email = 'guest@demo'").fetchone()
    if row:
        user = User(row[0], row[1])
    else:
        # Create one if missing
        cur = conn.execute(
            "INSERT INTO users (email,password_hash) VALUES (?,?)",
            ('guest@demo', '')
        )
        conn.commit()
        user_id = cur.lastrowid
        user = User(user_id, 'guest@demo')
    conn.close()

    # Log them in
    login_user(user)
    flash('Logged in as guest', 'info')
    return redirect(url_for('dashboard.dashboard'))


# Simple User class for Flask-Login
from flask_login import UserMixin
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email
