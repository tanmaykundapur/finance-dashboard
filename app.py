# app.py
from flask import Flask, render_template
from dashboard import dashboard_bp
from auth import auth_bp, LoginManager, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'replace-with-a-secure-random-value'
    app.config['DB_PATH'] = 'finances.db'

    # Setup Flask-Login
    login = LoginManager(app)
    login.login_view = 'landing'
    @login.user_loader
    def load_user(user_id):
        conn = __import__('auth').get_db()
        row = conn.execute("SELECT id,email FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        return User(row[0], row[1]) if row else None

    # Landing Page at /
    @app.route("/")
    def landing():
        return render_template("landing.html")

    # Auth routes under /auth
    app.register_blueprint(auth_bp,      url_prefix='/auth')
    # Dashboard routes under /dashboard
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
