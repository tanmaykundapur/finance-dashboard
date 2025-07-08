# dashboard.py
from flask import Blueprint, current_app, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import sqlite3, datetime, json

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    return sqlite3.connect(current_app.config['DB_PATH'])

@dashboard_bp.before_app_request
def init_db():
    """
    Ensure the users and tx tables exist, and tx has user_id.
    """
    conn = get_db()
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Create tx table if missing or without user_id
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY,
            date TEXT,
            cat TEXT,
            amt REAL
        )
    ''')
    # Add user_id column if it doesn't exist
    cursor = conn.execute("PRAGMA table_info(tx)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'user_id' not in columns:
        conn.execute('ALTER TABLE tx ADD COLUMN user_id INTEGER')
    conn.commit()
    conn.close()
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY,
            date TEXT,
            cat TEXT,
            amt REAL,
            user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Add/Edit
    if request.method == 'POST':
        d = request.form['date']
        c = request.form['cat']
        a = float(request.form['amt'])
        tx_id = request.form.get('id')
        conn = get_db()
        if tx_id:
            conn.execute('UPDATE tx SET date=?, cat=?, amt=? WHERE id=? AND user_id=?',
                         (d, c, a, tx_id, current_user.id))
        else:
            conn.execute('INSERT INTO tx (date,cat,amt,user_id) VALUES (?,?,?,?)',
                         (d, c, a, current_user.id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard.dashboard'))

    # Filters
    start = request.args.get('start')
    end = request.args.get('end')
    clauses, params = [], []
    clauses.append('user_id=?')
    params.append(current_user.id)
    if start:
        clauses.append('date>=?'); params.append(start)
    if end:
        clauses.append('date<=?'); params.append(end)
    where_sql = 'WHERE ' + ' AND '.join(clauses)

    # Edit prefill
    edit_id = request.args.get('edit')
    tx_to_edit = None
    if edit_id:
        conn = get_db()
        row = conn.execute(f'SELECT id,date,cat,amt FROM tx {where_sql} AND id=?',
                           params + [edit_id]).fetchone()
        conn.close()
        if row:
            tx_to_edit = dict(id=row[0], date=row[1], cat=row[2], amt=row[3])

    # Fetch rows
    conn = get_db()
    rows = conn.execute(
        f'SELECT id, date, cat, amt FROM tx {where_sql} ORDER BY date DESC LIMIT 10',
        params
    ).fetchall()
    summary = conn.execute(
        f'SELECT cat, SUM(amt) FROM tx {where_sql} GROUP BY cat',
        params
    ).fetchall()
    conn.close()

    cats, sums = zip(*summary) if summary else ([], [])
    chart_data = dict(labels=cats, data=sums)

    return render_template('dashboard.html', rows=rows, chart_data=json.dumps(chart_data), tx=tx_to_edit)

@dashboard_bp.route('/delete/<int:id>')
@login_required
def delete_tx(id):
    conn = get_db()
    conn.execute('DELETE FROM tx WHERE id=? AND user_id=?', (id, current_user.id))
    conn.commit(); conn.close()
    return redirect(url_for('dashboard.dashboard'))