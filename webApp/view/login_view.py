from flask import Blueprint, flash, flash, render_template, request, redirect, url_for, session, flash

from webApp.database.model import User
from webApp.database.manage_db import get_engine as engine
from webApp.database.model import get_session as Session
from webApp.database.manage_db import config, SESSION
from webApp.utility.email_temp import EmailTemplate

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
        
        if user and user.password == password:
            session['user'] = username
            session['session_id'] = config.ID(20)  # Generate a random session ID
            SESSION(user.email, 'create', session['session_id'])
            EmailTemplate.send_email(user.email, 'Welcome!', 'You have successfully registered.')
            return redirect(url_for('public_view.dashboard'))  # Redirect to a dashboard or home page
        else:
            flash('Invalid credentials. Please try again.')
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')

@login_view.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if len(password) < 8:
            error = 'Password must be at least 8 characters long.'
            return render_template('register.html', error=error)
        
        if username and password:
            # Replace with actual user creation logic
            return redirect(url_for('login_view.login'))
        else:
            error = 'Please fill in all fields.'
            return render_template('register.html', error=error)

    return render_template('register.html')

@login_view.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('session_id', None)
    SESSION(session.get('user'), 'delete', session.get('session_id'))
    return redirect(url_for('login_view.login'))
