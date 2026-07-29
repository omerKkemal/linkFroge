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