import os, requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods = ["POST", "GET"])
def index():
    return render_template("Login.html")

@app.route("/reader", methods=["POST", "GET"])
def reader():
    user_name_txt = request.form.get("user_name_txt")
    password_txt = request.form.get("password_txt")
    if db.execute("SELECT * FROM readers WHERE user_name = :user_name_txt AND password = :password_txt", {"user_name_txt": user_name_txt, "password_txt": password_txt}).rowcount == 0:
        return render_template("LogError.html", message="This User Name Does not Exists! Or Incorrect Password", bttn = "Try Again")

    if db.execute("SELECT user_name, cust_name, title, author, year FROM readers JOIN books ON books_id = books.id WHERE user_name = :user_name_txt", {"user_name_txt": user_name_txt}).rowcount == 0:
        readers = db.execute("SELECT * FROM readers WHERE user_name = :user_name_txt", {"user_name_txt": user_name_txt}).fetchone()
        return render_template("Reader.html", readers = readers, action = "Add a Book")

    readers = db.execute("SELECT user_name, cust_name, isbn, title, author, year FROM readers JOIN books ON books_id = books.id WHERE user_name = :user_name_txt", {"user_name_txt": user_name_txt}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "7isLrOkjqHxyy3d2FMXtXQ", "isbns": readers[2]})
    data = res.json()
    reviews_count = data['books'][0]['reviews_count']
    work_ratings_count = data['books'][0]['work_ratings_count']
    work_reviews_count = data['books'][0]['work_reviews_count']
    work_text_reviews_count = data['books'][0]['work_text_reviews_count']
    average_rating = data['books'][0]['average_rating']
    ratings_count = data['books'][0]["ratings_count"]
    text_reviews_count = data['books'][0]["text_reviews_count"]
    return render_template("Reader.html", readers = readers, action = "Change this Book", ratings_count = ratings_count, reviews_count = reviews_count, text_reviews_count = text_reviews_count, work_ratings_count = work_ratings_count, work_reviews_count = work_reviews_count, work_text_reviews_count = work_text_reviews_count, average_rating = average_rating)


@app.route("/register", methods=["POST"])
def register():
    return render_template("Register.html")

@app.route("/registerdn", methods=["POST"])
def registerdn():
    reader_user = request.form.get("user_name")
    if not db.execute("SELECT * FROM readers WHERE user_name = :user_name", {"user_name": reader_user}).rowcount == 0:
        return render_template("RegError.html", message="This User Name Already Exists!", bttn = "Try Again")

    user_name = request.form.get("user_name")
    password = request.form.get("password")
    cust_name = request.form.get("cust_name")
    db.execute("INSERT INTO readers (user_name, password, cust_name) VALUES (:user_name, :password, :cust_name)",
            {"user_name": user_name, "password": password, "cust_name": cust_name})
    db.commit()
    return render_template("RegSuccess.html")

@app.route("/reader/books/<user_name>", methods=["POST", "GET"])
def books(user_name):
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("Books.html", books = books, user_name = user_name)

@app.route("/reader/success/<user_name>/<int:book_id>", methods=["POST", "GET"])
def adding(user_name,book_id):
    books = db.execute("UPDATE readers SET books_id = :book_id WHERE user_name = :user_name", {"book_id": book_id, "user_name": user_name})
    db.commit()
    return render_template("AddSuccess.html", user_name = user_name)

@app.route("/reader/<user_name>", methods=["POST", "GET"])
def added(user_name):
    readers = db.execute("SELECT user_name, cust_name, title, author, year FROM readers JOIN books ON books_id = books.id WHERE user_name = :user_name_txt", {"user_name_txt": user_name}).fetchone()
    return render_template("Reader.html", readers = readers, action = "Change this Book")

@app.route("/dropping", methods=["POST"])
def dropping():
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("Books.html", books = books)
