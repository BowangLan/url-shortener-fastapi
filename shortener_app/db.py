import secrets
import uuid
from string import ascii_letters
from sqlalchemy.orm import Session
from . import models


def generate_url_key():
    return "".join([secrets.choice(ascii_letters) for _ in range(6)])


def create_new_db_url_object(target_url: str, key: str):
    """Create a new URL record for the database.

    Args:
        target_url (str): _description_
        key (str): _description_

    Returns:
        _type_: _description_
    """
    secret_key = str(uuid.uuid4())
    return models.URL(
        target_url=target_url,
        key=key,
        secret_key=secret_key
    )


def insert_new_url_record(db: Session, target_url: str) -> models.URL | None:
    key = generate_url_key()
    while get_active_url_by_key(db, key):
        key = generate_url_key()
    db_url = create_new_db_url_object(target_url, key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_active_url_by_key(db: Session, url_key: str) -> models.URL | None:
    """Get an active URL record by url key.

    Args:
        db (Session): the database session
        url_key (str): the url key

    Returns:
        models.URL | None: _description_
    """
    return db.query(models.URL).filter(models.URL.key ==
                                       url_key, models.URL.is_active).first()


def get_url_by_key(db: Session, url_key: str) -> models.URL | None:
    """Get the URL record by url key.

    Args:
        db (Session): _description_
        url_key (str): _description_

    Returns:
        models.URL | None: _description_
    """
    return db.query(models.URL).filter(models.URL.key == url_key).first()


def get_url_by_secret_key(db: Session, secret_key: str) -> models.URL | None:
    """Get the URL record by the secret key.

    Args:
        db (_type_): _description_
        secret_key (_type_): _description_

    Returns:
        _type_: _description_
    """
    return db.query(models.URL).filter(models.URL.secret_key ==
                                       secret_key).first()


def update_visit_count(db: Session, url_key: str):
    """Updates the visit count of a URL record given the urk key.

    Args:
        db (Session): the database session
        url_key (str): the url key

    Returns:
        Nonn or the updated URL object
    """
    db_url = get_active_url_by_key(db, url_key)
    if not db_url:
        return None
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url
