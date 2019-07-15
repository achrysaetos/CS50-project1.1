import os

from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import apis, random

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


@app.route("/home")
def home():
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("home.html", books=books)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/loginres", methods=["POST"])
def loginres():
    username=request.form.get("username")
    password=request.form.get("password")
    results=db.execute("SELECT * FROM users WHERE username=:username AND password=:password", 
                        {"username": username, "password": password}).fetchone()
    if results is None:
        return render_template("error.html")
    else:
        return render_template("home.html", results=results)

@app.route("/signupres", methods=["POST"])
def signupres():
    username=request.form.get("username")
    password=request.form.get("password")
    query=f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    results=db.execute(query)
    db.commit()
    return render_template("index.html", results=results)

@app.route("/complete_listing", methods=["GET", "POST"])
def complete_listing():
    query = f"SELECT * FROM books"
    results = db.execute(query).fetchall()
    return render_template("complete_listing.html", results=results, count=len(results))

@app.route("/feeling_crazy")
def feeling_crazy():
    query = f"SELECT * FROM books where id = {random.randint(1,5000)}"
    results = db.execute(query).fetchall()
    links=[]
    for r in results:
        links.append(apis.id_given_isbn(r.isbn))
    lookup = list(zip(results, links))
    return render_template("feeling_crazy.html", results=results, count=len(results), links=links, lookup=lookup)

@app.route("/results", methods=["POST"])
def results():
    name=request.form.get("name")
    query = f"SELECT * FROM books WHERE title LIKE '%{name}%' OR author LIKE '%{name}%' OR isbn LIKE '%{name}%' LIMIT 25"
    results = db.execute(query).fetchall()
    links=[]
    for r in results:
        links.append(apis.id_given_isbn(r.isbn))
    lookup = list(zip(results, links))
    return render_template("results.html", results=results, count=len(results), links=links, lookup=lookup)

@app.route("/selection/<string:isbn>", methods=["GET"])
def selection(isbn):
    query = f"SELECT * FROM books WHERE isbn='{isbn}'"
    results=db.execute(query).fetchall()
    stars=apis.reviews_given_isbn(isbn)
    stars_converted=float(stars['books'][0]['average_rating'])
    print(stars_converted)
    return render_template("selection.html", results=results, stars_converted=stars_converted)

@app.route("/api/books/<int:book_id>")
def book_api(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"Error."}), 422

    return jsonify({
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "year published": book.year
    })