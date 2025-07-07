# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3, datetime, json

app = Flask(__name__)
DB = 'finances.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
          CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY,
            date TEXT,
            cat TEXT,
            amt REAL
          )
        ''')

@app.route('/', methods=['GET','POST'])
def dashboard():
    init_db()

    # ——————————————————————
    # Handle form submission (add or edit)
    # ——————————————————————
    if request.method == 'POST':
        d = request.form['date']
        c = request.form['cat']
        a = float(request.form['amt'])
        tx_id = request.form.get('id')
        with sqlite3.connect(DB) as conn:
            if tx_id:
                conn.execute(
                    'UPDATE tx SET date=?, cat=?, amt=? WHERE id=?',
                    (d, c, a, tx_id)
                )
            else:
                conn.execute(
                    'INSERT INTO tx (date,cat,amt) VALUES (?,?,?)',
                    (d, c, a)
                )
        return redirect(url_for('dashboard'))

    # ——————————————————————
    # Date-range filter setup
    # ——————————————————————
    start = request.args.get('start')
    end   = request.args.get('end')
    where_clauses = []
    params = []
    if start:
        where_clauses.append("date >= ?")
        params.append(start)
    if end:
        where_clauses.append("date <= ?")
        params.append(end)
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # ——————————————————————
    # Handle edit pre-fill
    # ——————————————————————
    edit_id = request.args.get('edit')
    tx_to_edit = None
    if edit_id:
        with sqlite3.connect(DB) as conn:
            row = conn.execute(
                'SELECT id, date, cat, amt FROM tx WHERE id=?',
                (edit_id,)
            ).fetchone()
        if row:
            tx_to_edit = {'id': row[0], 'date': row[1], 'cat': row[2], 'amt': row[3]}

    # ——————————————————————
    # Fetch filtered rows & summary
    # ——————————————————————
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            f"SELECT id, date, cat, amt FROM tx {where_sql} "
            "ORDER BY date DESC LIMIT 10",
            params
        ).fetchall()
        summary = conn.execute(
            f"SELECT cat, SUM(amt) FROM tx {where_sql} GROUP BY cat",
            params
        ).fetchall()

    cats, sums = zip(*summary) if summary else ([], [])
    chart_data = {'labels': cats, 'data': sums}

    return render_template(
        'dashboard.html',
        rows=rows,
        chart_data=json.dumps(chart_data),
        tx=tx_to_edit
    )

@app.route('/delete/<int:id>')
def delete_tx(id):
    with sqlite3.connect(DB) as conn:
        conn.execute('DELETE FROM tx WHERE id = ?', (id,))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
