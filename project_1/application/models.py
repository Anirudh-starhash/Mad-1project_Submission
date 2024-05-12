from .database import db
from werkzeug.security import generate_password_hash,check_password_hash

class section(db.Model):
    __tablename__='section'
    section_id=db.Column(db.String,primary_key=True)
    title=db.Column(db.String)
    date=db.Column(db.String)
    description=db.Column(db.String,nullable=False)
    mange_for=db.relationship("librarian",secondary="manage")
    
class book_catalogue(db.Model):
    __tablename__='book_catalogue'
    auth_fname=db.Column(db.VARCHAR,nullable=False)
    auth_lname=db.Column(db.VARCHAR)
    title=db.Column(db.VARCHAR)
    publisher=db.Column(db.VARCHAR)
    year=db.Column(db.VARCHAR)
    ISBN_no=db.Column(db.VARCHAR,primary_key=True)
    section_id=db.Column(db.VARCHAR,db.ForeignKey(section.section_id))
    no_of_pages=db.Column(db.Integer)


class user(db.Model):
    __tablename__='user'
    user_id=db.Column(db.String(128),primary_key=True)
    user_fname=db.Column(db.String(128),nullable=False)
    user_lname=db.Column(db.String(128))
    user_email=db.Column(db.String(128))
    password=db.Column(db.String(128))
    has_copies=db.relationship("book_catalogue",secondary="book_issue")
    track_for=db.relationship("librarian",secondary="keeps_track_of")
    content=db.relationship("section",secondary="analysis")

class librarian(db.Model):
    __tablename__='librarian'
    librarian_id=db.Column(db.VARCHAR,primary_key=True)
    librarian_fname=db.Column(db.VARCHAR,nullable=False)
    librarian_lname=db.Column(db.VARCHAR)
    librarian_email=db.Column(db.VARCHAR)
    password=db.Column(db.VARCHAR)
    track_for=db.relationship("user",secondary="keeps_track_of")
    mange_for=db.relationship("section",secondary="manage")


    
class book_issue(db.Model):
    __tablename__='book_issue'
    id=db.Column(db.VARCHAR,db.ForeignKey(user.user_id),primary_key=True)
    ISBN_no=db.Column(db.VARCHAR,db.ForeignKey(book_catalogue.ISBN_no),primary_key=True)
    doi=db.Column(db.Date)
    count=db.Column(db.Integer)
    request_date=db.Column(db.Date)
    return_date=db.Column(db.Date)
    due_date=db.Column(db.Date)

class keeps_track_of(db.Model):
    __tablename__='keeps_track_of'
    librarian_id=db.Column(db.VARCHAR,db.ForeignKey(librarian.librarian_id),primary_key=True)
    user_id=db.Column(db.VARCHAR,db.ForeignKey(user.user_id),primary_key=True)

class manage(db.Model):
    librarian_id=db.Column(db.VARCHAR,db.ForeignKey(librarian.librarian_id),primary_key=True)
    section_id=db.Column(db.VARCHAR,db.ForeignKey(section.section_id),primary_key=True)
    
class reviews(db.Model):
      user_id=db.Column(db.VARCHAR,db.ForeignKey(user.user_id),primary_key=True)
      ISBN_no=db.Column(db.VARCHAR,db.ForeignKey(book_catalogue.ISBN_no),primary_key=True)
      feedback=db.Column(db.VARCHAR)
      rating=db.Column(db.Integer)
      
class role(db.Model):
    user_id=db.Column(db.VARCHAR,db.ForeignKey(user.user_id),primary_key=True)
    type=db.Column(db.VARCHAR)
    quota=db.Column(db.Integer)
    
class analysis(db.Model):
    user_id=db.Column(db.VARCHAR,db.ForeignKey(user.user_id),primary_key=True)
    section_id=db.Column(db.VARCHAR,db.ForeignKey(section.section_id),primary_key=True)
    count=db.Column(db.Integer)
    

