from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable= False)
    title = db.Column(db.String, nullable= False)
    author = db.Column(db.String, nullable= False)
    year = db.Column(db.String, nullable = False)


class user(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    hash = db.Column(db.String(128))
