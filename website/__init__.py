from flask import Flask
import mysql.connector
from mysql.connector import Error
from flask_login import LoginManager


# -------------------------------------------------
# Database Connection
# -------------------------------------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="yellowcpp2027",
            database="my_notes",
            autocommit=True
        )
        return connection
    except Error as err:
        print("❌ Database connection failed:", err)
        return None


# -------------------------------------------------
# App Factory
# -------------------------------------------------
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjahkjshkjdhjs'

    # -------------------------------------------------
    # Single DB connection
    # -------------------------------------------------
    app.db = get_db_connection()

    if app.db is None:
        print("⚠️ App started WITHOUT database connection")

    # -------------------------------------------------
    # Flask-Login setup
    # -------------------------------------------------
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        cursor = app.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            from .models import User
            return User(user_data)   # ✅ User object

        return None

    # -------------------------------------------------
    # Blueprints
    # -------------------------------------------------
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
