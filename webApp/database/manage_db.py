
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

from webApp.database.model import Base, SESSION_LOGIN
from webApp.utility.setting import Setting

config = Setting()
config.setting_var()

def get_engine():
    engine = create_engine(config.DB_URL, echo=config.DB_ECHO)
    Base.metadata.create_all(engine)
    return engine

engine = get_engine()

def get_session():
    Session = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
)
    return Session

Session = get_session()

def SESSION(user_email, flage, session_id=None):
    """
    Manage user sessions in the database.
    
    This function handles three main operations: creating new sessions, deleting existing sessions,
    and checking if a session exists for a user. It interacts with the SESSION_LOGIN database model
    to persist session information.
    
    Args:
        user_email (str): The email address of the user for which to manage the session.
        flage (str): The operation to perform on the session. Valid values are:
            - 'create': Create a new session entry for the user.
            - 'delete': Delete an existing session entry for the user.
            - 'check': Check if a session exists for the user.
        session_id (str, optional): The session ID to use. Defaults to None.
            - For 'create': If not provided, a new random ID is generated using config.ID(20).
            - For 'delete' and 'check': Must be provided to match against the database.
    
    Returns:
        bool: The result of the operation:
            - For 'create': True if the session was successfully created, False otherwise.
            - For 'delete': True if the session was successfully deleted, False otherwise.
            - For 'check': True if a session exists for the user, False otherwise.
            - For invalid flage values: False.
    
    Raises:
        No exceptions are explicitly raised. Database errors are handled internally by SQLAlchemy.
    
    Examples:
        >>> # Create a new session for a user
        >>> SESSION('user@example.com', 'create', 'session_123')
        True
        
        >>> # Check if a session exists
        >>> SESSION('user@example.com', 'check', 'session_123')
        True
        
        >>> # Delete a session
        >>> SESSION('user@example.com', 'delete', 'session_123')
        True
    
    Notes:
        - The function uses SQLAlchemy ORM for database operations.
        - Each operation creates a new SessionLocal instance for database interaction.
        - The 'delete' operation uses filter_by to find and remove matching sessions.
        - The 'create' operation generates a random ID if session_id is not provided.
        - The 'check' operation returns the first matching record or False if none found.
    """
    _session = Session()
    if flage == 'delete':
        _session.query(SESSION_LOGIN).filter_by(
            email=user_email,
            session_id=session_id
        ).delete()
        _session.commit()
        return True
    elif flage == 'create':
        new_session = SESSION_LOGIN(
            ID=config.ID(10), 
            email=user_email, 
            session_id=session_id or config.ID(20)
        )
        _session.add(new_session)
        _session.commit()
        _session.close()
        return True
    elif flage == 'check':
        is_login = _session.query(SESSION_LOGIN).filter_by(
            email=user_email,
            session_id=session_id
        ).first()
        if is_login:
            return True
        else:
            return False
    else:
        return False


def create_all_tables():
    """
    Create all tables defined in the SQLAlchemy models.

    This function initializes the database schema by creating all tables defined in the SQLAlchemy
    models. It uses the engine created by the `get_engine` function to connect to the database and
    create the tables.

    Returns:
        None
    """
    Base.metadata.create_all(get_engine())
    print("All tables created successfully.")
