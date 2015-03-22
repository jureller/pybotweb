from functools import partial
from pybot.db.dbmodel import (db, User, Page, 
                                Message, MessageType,
                                Link)

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

def add_to_db(obj: db.Model) -> bool:
    db.session.add(obj)
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def remove_from_db(obj: db.Model):
   db.session.delete(obj)
   db.session.commit()

def create_user(email=None, first_name=None, last_name=None, password=None) -> bool:
    new_user = User(email, first_name, last_name)
    new_user.password = password
    return add_to_db(new_user)

def get_user(userid=None, email=None, first_name=None, last_name=None) -> User:
    if userid:
        f = partial(User.query.filter_by, id=userid)
    elif email:
        f = partial(User.query.filter_by, email=email)
    elif first_name:
        f = partial(User.query.filter_by, first_name=first_name)
    elif last_name:
         f = partial(User.query.filter_by, last_name=last_name)
    else:
        return None

    return f().first()

def change_user(email: str, **kwargs):
    user = get_user(email=email)
    if 'new_email' in kwargs:
        user.email = kwargs['new_email']
        del kwargs['new_email']
    for k, v in kwargs.items():
        user.__setattr__(k, v)
    db.session.commit()

def delete_user(email: str):
    user = get_user(email=email)
    remove_from_db(user)

def create_page(title: str, content: str):
    new_page = Page(title, content)
    add_to_db(new_page)

def get_page(title: str) -> Page:
    page = Page.query.filter_by(title=title).first()
    return page 

def change_page(title: str, **kwargs):
    page = get_page(title)
    if 'new_title' in kwargs:
        page.title = kwargs['new_title']
        del kwargs['new_title']
    for k, v in kwargs.items():
        page.__setattr__(k, v)
    db.session.commit()       

def delete_page(title: str):
    page = get_page(title)
    remove_from_db(page)


def get_header() -> Message:
    try:
        header = Message.query.filter_by(
            message_type=MessageType.header).first()
    except NoResultFound:
        header = None
    return header

def set_header(text: str):
    current_header = get_header()
    if current_header:
        Message.query.filter_by(
                            message_type=MessageType.header).update({Message.text: text})
        db.session.commit()
    else:
        new_header = Message(MessageType.header, text)
        add_to_db(new_header)

def get_footer() -> Message:
    try:
        footer = Message.query.filter_by(
                            message_type=MessageType.footer).first()
    except NoResultFound:
        footer = None
    return footer

def set_footer(text: str) -> bool:
    current_footer = get_footer()
    if current_footer:
        Message.query.filter_by(
                            message_type=MessageType.footer).update({Message.text: text})
        db.session.commit()
    else:
        new_footer = Message(MessageType.footer, text)
        return add_to_db(new_footer)

def add_link(text: str, endpoint='', variable='') -> bool:
    new_link = Link(text, endpoint, variable)
    return add_to_db(new_link)

def get_links() -> [Link]:
    try:
        return Link.query.all()
    except Exception: # change to the actual exception
        return []

def remove_link(text: str) -> bool:
    try:
        link = Link.query.filter_by(text=text).first()
    except NoResultFound:
        return False
    remove_from_db(link)
    return True

