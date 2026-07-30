"""
This module defines the Setting class, which encapsulates application-wide configurations and settings.
It includes methods for generating secure keys, managing paths for logs and databases, and handling email configurations.
The class is designed to work seamlessly in both development and PyInstaller bundled environments.

functions:
- __init__: Initializes the Setting instance and prepares necessary directories.
- setting_var: Sets up all configuration variables including secret keys, paths, and email settings.

howtouse:
1. Import the Setting class from this module.
2. Create an instance of the Setting class to access configurations.

Example:
from utility.setting import Setting

# Initialize settings and set variables
config = Setting()
config.setting_var()

"""

import sys
import os
import secrets
import string
import tempfile
import filelock
from datetime import datetime


class Setting:
    """
    The Setting class handles application-wide configurations such as:
    - Secure key generation
    - Logging and database paths
    - SMTP/email settings
    - Default flags and modes
    This version ensures safe handling across dev and PyInstaller builds.
    """

    def __init__(self):
        """
        Constructor to initialize all settings and prepare directories.
        Called automatically when `Setting()` is instantiated.
        """
        self.setting_var()
        self._initialize_paths()

    def _initialize_paths(self):
        """
        Ensures required directories for logs and database are created.
        """
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.DB_DIR, exist_ok=True)

    def _resolve_path(self, relative_path):
        """
        Resolves an absolute path that works during both development and
        when running as a PyInstaller bundle.
        Args:
            relative_path (str): Path relative to project root or bundle.
        Returns:
            str: Absolute path resolved from base directory.
        """
        if hasattr(sys, '_MEIPASS'):  # PyInstaller bundled mode
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def setting_var(self):
        """
        Initializes all configuration variables including:
        - Application secret key
        - Log and database paths
        - Email configuration
        - Other constants and flags
        - This method is called during the class initialization to set up the environment.
        """

        # Generate a strong secret key
        self.SECRAT_KEY = ''.join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(100)
        )

        # Use temp directory to ensure writable location (for PyInstaller)
        # self.APP_DIR = os.path.join(tempfile.gettempdir(), "SpecterPanel")

        # Set up directory structure
        # self.DB_DIR = os.path.join(self.APP_DIR, "db")
        # self.LOG_DIR = os.path.join(self.APP_DIR, "logs")
        self.DB_DIR = "webApp/database"
        self.LOG_DIR = "webApp/logs"

        # Logging configuration
        self.LOG_FILE_NAME = "log.txt"
        self.LOG_FILE_PATH = os.path.join(self.LOG_DIR, self.LOG_FILE_NAME)

        # Database configuration
        self.DB_NAME = "linkFroge.db"
        self.DB_URI = f"sqlite:///{os.path.join(self.DB_DIR, self.DB_NAME)}"
        self.DB_ECHO = False  # Set to True for SQLAlchemy query logging

        # JSON file for user data or configuration
        self.JSON_FILE_PATH = os.path.join(self.DB_DIR, "info.json")

        # Admin email setup
        self.ADMIN_EMAIL = 'omerkemal2019@gmail.com'
        self.EMAIL_PASSWORD = 'kbac agov frve pwhh'  # TODO: Replace with env or config file
        self.EMAIL = 'omerkemal2019@gmail.com'
        self.SMTP_USE_TLS = True
        self.SMTP_LINK = 'smtp.gmail.com'
        self.SMTP_PORT = 587
        self.EMAIL_TYPE = "html"

        self.ENCRYPTION_KEY = b'W\xb7a\xab\xf7\xd9\xd2\xf0\x8b\xcb\xea\xc3\x93G\xbdS'  # TODO: Replace with a secure key and store it in the db

        # static file paths
        self.STATIC_DIR = "/"
        self.PYLOADS = os.listdir(self.STATIC_DIR)

        # Application behavior settings
        self.CATEGORY = {
            "hacking": "For when you want to feel like a 1337 hax0r but really just forgot your password",
            "phishing": "Because scamming grandmas is totally ethical (It's not. Don't do it.)",
            "malware": "The digital equivalent of giving someone a cold. Except worse.",
            "spam": "For emails that nobody asked for. Like that one relative who forwards everything.",
            "social_engineering": "Manipulating humans since before it was cool. Also known as 'talking'.",
            "exploit_dev": "Breaking things so you can fix them. Or break them more. Your choice.",
            "reverse_engineering": "Taking things apart to see how they work. Like a toddler with a remote control.",
            "forensics": "Digital detective work. Because someone always leaves a trail of digital cookies.",
            "cryptography": "The art of writing secrets that even you can't remember. Also known as 'password reset hell'.",
            "network_analysis": "Watching ones and zeros fly by. Like watching paint dry, but with more blinking lights.",
            "osint": "Creeping on people professionally. Also known as 'research' when HR is watching.",
            "ctf": "Capture The Flag. Like a treasure hunt, but with more caffeine and existential dread.",
            "red_team": "Pretending to be the bad guy. With permission. And snacks. Usually.",
            "blue_team": "Pretending to be the good guy. With a firewall and a prayer.",
            "purple_team": "When red and blue teams hold hands and work together. It's as rare as a unicorn.",
            "social_media": "Because your personal data is their business model. And they're very good at it.",
            "cloud_security": "Securing someone else's computer in someone else's basement. But it's 'the cloud' so it sounds cool.",
            "iot": "Internet of Things. Because your toaster didn't need to be on the internet, but here we are.",
            "mobile_security": "Securing the device you literally sleep with. No judgment. We all do it.",
            "blockchain": "The solution to problems you didn't know you had. Also, funny money.",
            "zero_day": "Find a bug, tell no one, get paid. Or get arrested. It's a coin flip really.",
            "ransomware": "Digital kidnapping. Don't pay. Nobody pays. We're definitely lying.",
            "ddos": "The digital equivalent of 10,000 people knocking on your door at once. Very effective. Very rude.",
            "penetration_testing": "Breaking into buildings. Digitally. With permission. Usually.",
            "threat_intel": "Knowing what the bad guys are doing before they do it. Like a digital psychic.",
            "incident_response": "What to do when everything goes to hell. Step 1: Panic. Step 2: Pretend you planned for this.",
            "compliance": "Pretending to be secure so auditors leave you alone. The official IT pastime.",
            "training": "Teaching humans to not click on obvious phishing links. It's like herding cats. But harder.",
            "consulting": "Telling people what to do. Very expensive. Usually ignored.",
            "management": "Managing people who know more than you. Good luck with that.",
            "research": "Reading PDFs so you don't have to. You're welcome.",
            "privacy": "The thing that doesn't exist anymore. But we still pretend it does.",
            "data_breach": "When data gets out. Like a clown car door opening. Everyone runs.",
            "auth": "Passwords. We all hate them. We all use them. We all use 'password'.",
            "api": "Acronyms Permeating Interfaces. Also known as 'why won't this damn thing work'.",
            "automation": "Making computers do your job so you can watch cat videos. The dream.",
            "devops": "Developers and ops having a baby. And that baby is CI/CD. And it's crying.",
            "container": "Shipping containers for code. You can stack them. Unlike your code.",
            "serverless": "No servers. Just magic. And other people's servers you don't have to manage.",
            "microservices": "Breaking your app into tiny pieces so it can break in more interesting ways.",
            "legacy": "Code older than you. Touching it means waking the ancient ones. And they are angry.",
            "database": "Where data goes to sleep. And sometimes never wakes up.",
            "frontend": "The part users see. The part that makes you want to scream at your browser.",
            "backend": "The part nobody sees. The part that actually works. Most of the time.",
            "fullstack": "Both frontend and backend. Also known as 'I make double the money for double the pain'.",
            "ai": "Artificial Intelligence. Or as I call it, 'expensive pattern matching'.",
            "ml": "Machine Learning. Teaching computers to be wrong. But faster.",
            "deep_learning": "Machine learning but with more layers. Like a digital onion. And it makes you cry too.",
            "nlp": "Natural Language Processing. Teaching computers to understand you. They still don't.",
            "computer_vision": "Teaching computers to see. They're still squinting.",
            "robotics": "Making metal humans. Hopefully they won't kill us. Probably will. Maybe.",
            "quantum": "Computing that works on a fundamental level. Also known as 'I have no idea what's happening'.",
            "hardware": "The stuff you can touch. And break. Easily. Very expensive.",
            "embedded": "Computers in things that shouldn't have computers. Your fridge. Your car. Your toothbrush.",
            "firmware": "Software that's too stubborn to move. Lives in hardware. Never leaves. Ever.",
            "protocols": "The rules computers play by. They cheat. Rules are more like... guidelines.",
            "networking": "Connecting computers so they can ignore each other in new and exciting ways.",
            "wireless": "Networking but you can't see the wires. Magic. Terrible, unreliable magic.",
            "dns": "The phonebook of the internet. Except entries change when you're not looking.",
            "vpn": "Pretending you're in another country. Also known as 'watching Netflix in another timezone'.",
            "proxy": "Having someone else get things for you. Like a digital assistant. With no boundaries.",
            "firewall": "Digital wall. Doesn't stop everything. But it tries. It really does.",
            "ids": "Intrusion Detection System. Screams when someone's inside. Like a really expensive alarm clock.",
            "ips": "Intrusion Prevention System. Stops people from getting in. Most of the time. Usually. Maybe.",
            "siem": "Security Information and Event Management. Collecting logs so you can never read them.",
            "soar": "Security Orchestration, Automation, and Response. Automating responses so you can play video games.",
            "edr": "Endpoint Detection and Response. It's like a guard dog for your computer. A very expensive guard dog.",
            "xdr": "Extended Detection and Response. It's like EDR but bigger. More expensive too.",
            "zero_trust": "Trust no one. Not even yourself. Especially not yourself.",
            "iam": "Identity and Access Management. Knowing who is who. And sometimes still getting it wrong.",
            "rbac": "Role Based Access Control. Giving people permissions based on their job. Surprisingly complicated.",
            "mfa": "Multi-Factor Authentication. Because your password wasn't enough. Need to prove you have a phone too.",
            "sso": "Single Sign-On. One password to rule them all. Unless you forget it. Then you're doomed.",
            "password": "The thing that makes the internet work. Also the thing that makes everyone angry. All the time.",
            "encryption": "Making data unreadable. So that nobody can read it. Including you, if you lose the key.",
            "decryption": "Making encrypted data readable. Assuming you remember the key. Good luck.",
            "hash": "Digital fingerprint. Irreversible. Like a tattoo. But for data.",
            "salt": "Random data added to hashes. Not the kind you put on your food. Don't eat it.",
            "certificate": "Digital ID card. Expires regularly. Just like your real ID. And causes similar stress.",
            "key": "The thing that unlocks encryption. Or locks it. Depends. Very powerful. Very scary.",
            "secret": "Something you don't tell anyone. That's why it's called a secret. Duh.",
            "token": "Digital key. Usually changes. Sometimes doesn't. Keeps you guessing.",
            "jwt": "JSON Web Token. A string with a lot of stuff in it. Very trendy. Very secure. Until it's not.",
            "oauth": "Open Authorization. Letting other things access things. With permission. Usually.",
            "oidc": "OpenID Connect. Like OAuth but more complex. Because we needed more complexity.",
            "saml": "Security Assertion Markup Language. Old. XML. Still works. Somehow.",
            "ldap": "Lightweight Directory Access Protocol. Not lightweight. Not simple. But we use it anyway.",
            "active_directory": "Microsoft's directory service. The source of all headaches. And all permissions."
        }
        self.DEBUG_MODE = True
        self.HOST = "0.0.0.0"
        self.PORT = 5000
        self.OPENROUTER_API_URL_MODELS_LIST = "https://openrouter.ai/api/v1/models"


    def ID(self, n=5):
        """
        Generates a random alphanumeric ID of specified length.
        Args:
            n (int): Length of the ID (default is 5)
        Returns:
            str: A randomly generated ID
        """
        return ''.join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(n)
        )
    def log(self, event):
        """
            Records an event in the application log file with a timestamp.
            The event is appended to a log file with a date and time when it occurred.

            A file lock is used to prevent simultaneous access to the log file, ensuring
            thread safety when logging events.

            Args:
                event (str): The event message that describes the action or occurrence.
        """
        # Use file lock to prevent concurrent access to the log file
        lock = filelock.FileLock('counter.lock')
        event_rec = datetime.now()  # Capture the current timestamp

        with lock:
            # Open the log file in append mode and write the event with timestamp
            with open(self.LOG_FILE_PATH, "a") as f:
                f.write(f"[  {str(event_rec)}  ] : {str(event)}\n")