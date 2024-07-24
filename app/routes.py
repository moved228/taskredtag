from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Author, Book
import io
import csv
from flask import Response

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/books')
def view_books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        year = request.form['year']
        author_id = request.form['author_id']
        
        new_book = Book(title=title, genre=genre, year=year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        
        return redirect(url_for('main.view_books'))
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.genre = request.form['genre']
        book.year = request.form['year']
        book.author_id = request.form['author_id']
        
        db.session.commit()
        return redirect(url_for('main.view_books'))
    authors = Author.query.all()
    return render_template('edit_book.html', book=book, authors=authors)

@bp.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('main.view_books'))

@bp.route('/filter_books', methods=['GET'])
def filter_books():
    title = request.args.get('title', '')
    author_name = request.args.get('author', '')
    books = Book.query.join(Author).filter(
        (Book.title.ilike(f'%{title}%')) & (Author.name.ilike(f'%{author_name}%'))
    ).all()
    return render_template('books.html', books=books)

@bp.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        
        new_author = Author(name=name)
        db.session.add(new_author)
        db.session.commit()
        
        return redirect(url_for('main.view_books'))
    return render_template('add_author.html')

@bp.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author_id).all()
    for book in books:
        db.session.delete(book)
    db.session.delete(author)
    db.session.commit()
    return redirect(url_for('main.view_books'))

@bp.route('/authors')
def view_authors():
    authors = Author.query.all()
    return render_template('authors.html', authors=authors)


@bp.route('/export_books')
def export_books():
    books = Book.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Title', 'Genre', 'Year', 'Author'])
    
    for book in books:
        writer.writerow([
            book.id,
            book.title,
            book.genre,
            book.year,
            book.author.name
        ])
    
    output.seek(0)
    
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=books.csv"
    
    return response