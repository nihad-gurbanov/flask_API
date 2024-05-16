# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_date = db.Column(db.Date)
    genre = db.Column(db.String(50))
    isbn = db.Column(db.String(20), unique=True)

    def __repr__(self):
        return f"<Book {self.title}>"
