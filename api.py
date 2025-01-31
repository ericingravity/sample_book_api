import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100))

with app.app_context():
    db.create_all()  # Create database


@app.route("/books", methods=["GET"])
def get_books():
    title_query = request.args.get("title")
    author_query = request.args.get("author")

    query = Book.query
    if title_query:
        query = query.filter(Book.title.ilike(f"%{title_query}%"))
    if author_query:
        query = query.filter(Book.author.ilike(f"%{author_query}%"))

    books = query.all()
    book_list = [{"id": book.id, "title": book.title, "author": book.author} for book in books]
    return jsonify(book_list)


@app.route("/books", methods=["POST"])
def create_book():
    new_book_data = request.get_json()

    title = new_book_data.get("title")
    author = new_book_data.get("author")

    if not isinstance(title, str) or not isinstance(author, str):
        return jsonify({"error": "Title and author must be strings"}), 400

    existing_book = Book.query.filter_by(title=title, author=author).first()
    if existing_book:
        return jsonify({"error": "Book and author combination already exist"}), 400

    new_book = Book(title=new_book_data["title"], author=new_book_data.get("author"))
    db.session.add(new_book)
    db.session.commit()
    return jsonify({
        "message": "Book added",
        "book": {"id": new_book.id, "title": new_book.title, "author": new_book.author}
        }), 201


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):

    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book ID not found: " + str(book_id)}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book ID " + str(book_id) + " deleted"}), 200


@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book_non_int(book_id):
    return jsonify({"error": "Unknown book ID type: " + str(book_id)}), 404


if __name__ == "__main__":
   app.run(port=5000)
