from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, password, first_name=None):
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = current_app.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            if check_password_hash(user_data['password'], password):
                user_obj = User(
                    id=user_data['id'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name')
                )
                login_user(user_obj, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/sign-up', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        cursor = current_app.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hashed_password = generate_password_hash(password1, method='scrypt')

            cursor.execute(
                "INSERT INTO users(email, first_name, password) VALUES(%s, %s, %s)",
                (email, first_name, hashed_password)
            )
            current_app.db.commit()  # commit on connection
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            new_user_data = cursor.fetchone()
            cursor.close()

            new_user = User(
                id=new_user_data['id'],
                email=new_user_data['email'],
                password=new_user_data['password'],
                first_name=new_user_data.get('first_name')
            )
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign-up.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
