from flask import Flask, request, jsonify, render_template
from models import db, Book
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_books.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

# Combined endpoint for getting books with search, sorting, pagination, and filtering
@app.route('/books', methods=['GET'])
def get_books():
    # Search and filter parameters
    title_query = request.args.get('title')
    author_query = request.args.get('author')
    genre_query = request.args.get('genre')
    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')

    # Sorting parameters
    sort_by = request.args.get('sort_by', 'title')  # Default sort by title
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order ascending

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Default 10 books per page

    # Query building
    books_query = Book.query
    if title_query:
        books_query = books_query.filter(Book.title.like(f"%{title_query}%"))
    if author_query:
        books_query = books_query.filter(Book.author.like(f"%{author_query}%"))
    if genre_query:
        books_query = books_query.filter(Book.genre.like(f"%{genre_query}%"))
    if start_year and end_year:
        start_date = datetime.strptime(start_year, '%Y').date()
        end_date = datetime.strptime(end_year, '%Y').date()
        books_query = books_query.filter(Book.publication_date.between(start_date, end_date))

    # Sorting
    if sort_order == 'desc':
        books_query = books_query.order_by(getattr(Book, sort_by).desc())
    else:
        books_query = books_query.order_by(getattr(Book, sort_by))

    # Pagination
    books_pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)
    books = books_pagination.items

    # Format books for JSON response
    books_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'publication_date': book.publication_date.strftime('%Y-%m-%d'),
        'genre': book.genre,
        'isbn': book.isbn
    } for book in books]

    return jsonify({
        'books': books_list,
        'total': books_pagination.total,
        'pages': books_pagination.pages,
        'current_page': page
    })


# Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Media Type: Please send data in JSON format'}), 415

    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        publication_date=datetime.strptime(data['publication_date'], '%Y-%m-%d').date(),
        genre=data['genre'],
        isbn=data['isbn']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201


# Update an existing book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Media Type: Please send data in JSON format'}), 415

    data = request.get_json()
    book = Book.query.get(id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    book.title = data['title']
    book.author = data['author']
    book.publication_date = datetime.strptime(data['publication_date'], '%Y-%m-%d').date()
    book.genre = data['genre']
    book.isbn = data['isbn']
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

# Delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
