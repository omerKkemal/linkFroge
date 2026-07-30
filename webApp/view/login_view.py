from flask import Blueprint, flash, flash, render_template, request, redirect, url_for, session, flash, jsonify
import traceback
import requests

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


@login_view.route('/<url>/<ID>')
def cheack_if_the_url_alive(url, ID):
    session_manager = Session()
    try:
        if session_manager.query(service_linkes).filter_by(service_linke=url, ID=ID).first():
            r = requests.head(url, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                return jsonify({"message": "the link stile alive(for now)"}), 200
            else:
                return jsonify({"message": "sudden the link is death my condolence"}),404 
    except Exception as e:
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        session_manager.rollback()
        return redirect("login_view.index")
    finally:
        session_manager.close()

@login_view.route('/public_links')
def public_link():
    """
    Displays all public links for users to view and access.
    What it does:
    - Queries the database for all links with visibility set to 'public'
    - Renders the public_links.html template with the list of public links
    - Only allows GET requests (POST/PUT/DELETE are rejected)
    Returns:
    - Rendered 'public_liks.html' template with public links for GET requests
    - HTML error page for non-GET requests
    """
    session_manager = Session()
    
    # Only allow GET requests
    if request.method != "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Method Not Allowed - FrogLink</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e, #16213e);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                    padding: 20px;
                }
                .error-container {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    max-width: 500px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    border: 2px solid #4CAF50;
                }
                .error-icon {
                    font-size: 64px;
                    margin-bottom: 20px;
                }
                .error-title {
                    color: #c62828;
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .error-message {
                    color: #555;
                    font-size: 16px;
                    margin-bottom: 20px;
                    line-height: 1.6;
                }
                .error-frog {
                    font-size: 48px;
                    margin: 15px 0;
                }
                .back-btn {
                    display: inline-block;
                    background: linear-gradient(135deg, #4CAF50, #43A047);
                    color: white;
                    padding: 12px 30px;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }
                .back-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
                }
                .sarcastic {
                    color: #888;
                    font-style: italic;
                    font-size: 14px;
                    margin-top: 15px;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">🚫</div>
                <div class="error-title">Method Not Allowed</div>
                <div class="error-message">
                    Oops! You're not supposed to be here.<br>
                    This page only accepts GET requests.<br>
                    <span style="font-size: 14px; color: #999;">(What were you trying to do? Hack us? Nice try.)</span>
                </div>
                <div class="error-frog">🐸</div>
                <a href="/public_links" class="back-btn">Go Back</a>
                <div class="sarcastic">"Try again. But this time, don't break it."</div>
            </div>
        </body>
        </html>
        """, 405
    
    try:
        all_public_link = session_manager.query(service_linkes).filter_by(visibility="public").all()
        return render_template('public_liks.html', all_public_link=all_public_link)
    except Exception as e:
        print(f"Error fetching public links: {e}")
        flash("Error loading public links. Please try again.", "error")
        return render_template('public_liks.html', all_public_link=[])
    finally:
        session_manager.close()

