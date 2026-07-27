from flask import Blueprint, flash, flash, render_template, request, redirect, url_for, session, flash
import traceback

from database.model import User, service_linkes
from database.manage_db import get_engine as engine
from database.manage_db import Session
from database.manage_db import config, SESSION
from utility.email_temp import EmailTemplate

login_view = Blueprint(
    'login_view',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

# home page route
@login_view.route('/')
def index():
    return render_template('index.html')

@login_view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Session().query(User).filter_by(username=username).first()
        
        if user and user.password_hash == password:
            session['user'] = username
            session['session_id'] = config.ID(20)  # Generate a random session ID
            SESSION(user.username, 'create', session['session_id'])
            return redirect(url_for('auth_view.dashboard'))  # Redirect to a dashboard or home page
        else:
            flash('Invalid credentials. Please try again.')
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')

@login_view.route('/register', methods=['GET', 'POST'])
def register():
    email_bot = EmailTemplate('https://linkfroge.com')
    session = Session()  # Create a new session for database operations
    try:    
        if request.method == 'POST':
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            display_name = request.form.get('display_name')

            if len(password) < 8:
                error = 'Password must be at least 8 characters long.'
                return render_template('register.html', error=error)
            
            if username and password:
                existing_user = session.query(User).filter_by(username=username).first()
                if existing_user:
                    error = 'Username already exists. Please choose a different one.'
                    return render_template('register.html', error=error)

                token = f"linkFrog-v1-sp{config.ID(30)}"  # Generate a random token for the user
                try:
                    new_user = User(username=username, display_name=display_name, email=email, password_hash=password, token=token)
                    session.add(new_user)
                    session.commit()
                    welcom_email = 'Welcome to LinkFroge'
                    email_bot.send_email(welcom_email, email_bot.welcome_email(username, email), email)
                    print(f"New user registered: {new_user}")
                    return redirect(url_for('login_view.login'))
                except Exception as e:
                    print(f"Error during user registration: {traceback.format_exc()}")
                    session.rollback()  # Rollback the session in case of an error
                    error = 'An error occurred during registration. Please try again.'
                    return render_template('register.html', error=error)
            else:
                error = 'Please fill in all fields.'
                return render_template('register.html', error=error)

        return render_template('register.html')
    except Exception as e:
        print(f"Error during registration: {e}")
        error = 'An error occurred during registration. Please try again.'
        Session().rollback()  # Rollback the session in case of an error
        return render_template('register.html', error=error)
    finally:
        Session().close()

@login_view.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('session_id', None)
    SESSION(session.get('user'), 'delete', session.get('session_id'))
    return redirect(url_for('login_view.login'))


@login_view.route('/contact', methods=['POST'])
def contact():
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    if not all([email, subject, message]):
        return render_template('index.html', contact_error='Please fill in all fields.')
    
    # Here you can send an email, save to database, or whatever you want
    # For now, just show success message
    return render_template('index.html', contact_success='Thank you for your message! We\'ll get back to you soon. 🐸')


@login_view.route("/<ID>")
def load_dynmic_link(ID):
    session = Session()
    try:
        to_be_loaded_link = session.query(service_linkes).filter_by(ID=ID).first()
        return render_template("ifram.html", service_link=to_be_loaded_link.service_link)
    except Exception as e:
        print(str(e))
        error = 'No such link ;('
        return render_template('index.html',error=error)

