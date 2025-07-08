# app.py
from flask import Flask
from dashboard import dashboard_bp
from auth import auth_bp, LoginManager, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'replace-with-a-secure-random-value'
    app.config['DB_PATH'] = 'finances.db'

    # Setup Flask-Login
    login = LoginManager(app)
    login.login_view = 'auth.login'
    @login.user_loader
    def load_user(user_id):
        # Re-create the User object from its ID
        conn = __import__('auth').get_db()
        row = conn.execute("SELECT id,email FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        return User(row[0], row[1]) if row else None

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
