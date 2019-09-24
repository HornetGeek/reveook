import os

from flask import Flask, session , render_template , request ,redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

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


@app.route("/" , methods=['post','get'])
def index():
    return render_template("index.html")
    

@app.route("/signup" , methods=['post','get'])
def signup():
    
    if request.method == 'GET   ':
        return render_template('index.html')
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    if db.execute("SELECT * FROM users WHERE email=:email",{"email":email}).rowcount == 1:
        return "<h1>please try another email or username</h1>"
        
    db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", {"username": username, "password": password,"email": email})
        
    db.commit()
    return redirect(url_for('signin'))


@app.route("/signin", methods=['post','get'])
def signin():
    if request.method == 'GET':
        session.clear()
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        if db.execute("SELECT * FROM users WHERE email=:email AND password = :password", {"email":email, "password":password}).rowcount == 1:
            
            user_id = db.execute("Select user_id FROM users WHERE email=:email", {"email":email}).fetchone()
            session["user_id"] = user_id[0]
            db.commit()
            return redirect("home")
        else:
            return "it doesn't match please try again"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route('/home', methods=['post','get'])
def home():
    if request.method == 'GET':
        if session:
            title = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":2}).fetchone()[0]
            author = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":2}).fetchone()[0]
            isbn = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":2}).fetchone()[0]

            title1 = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":3}).fetchone()[0]
            author1 = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":3}).fetchone()[0]
            isbn1 = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":3}).fetchone()[0]

            title2 = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":4}).fetchone()[0]
            author2 = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":4}).fetchone()[0]
            isbn2 = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":4}).fetchone()[0]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

            title3 = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":5}).fetchone()[0]
            author3 = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":5}).fetchone()[0]
            isbn3 = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":5}).fetchone()[0]

            title4 = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":6}).fetchone()[0]
            author4 = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":6}).fetchone()[0]
            isbn4 = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":6}).fetchone()[0]

            title5 = db.execute("SELECT title FROM books WHERE book_id=:i",{"i":7}).fetchone()[0]
            author5 = db.execute("SELECT author FROM books WHERE book_id=:i",{"i":7}).fetchone()[0]
            isbn5 = db.execute("SELECT isbn FROM books WHERE book_id=:i",{"i":7}).fetchone()[0]
            
            return render_template("home.html", i = 1, title=title, author=author,isbn=isbn, title1=title1, author1=author1,isbn1=isbn1, title2=title2, author2=author2,isbn2=isbn2, title3=title3, author3=author3,isbn3=isbn3, title4=title4, author4=author4,isbn4=isbn4, title5=title5, author5=author5,isbn5=isbn5)
        else:
            return redirect(url_for("signin"))
@app.route("/search", methods=["post","get"])
def search():
    if session:
        book_k = "%" + request.args.get("search") + "%"
        book_k = book_k.title()
        geterBook = db.execute('SELECT isbn, title, author, year FROM books WHERE \
        isbn LIKE :book_k OR \
        title LIKE :book_k OR \
        author LIKE :book_k', {"book_k":book_k})
        
        if geterBook.rowcount == 0:
            return "we can't find books with that description."
        geterBook = geterBook.fetchall()
        return render_template("search.html", geterBook=geterBook)
    else:
        return redirect(url_for("signin"))


@app.route("/book/<isbn>", methods=["post", "get"])
def book(isbn):
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"K22LwhtLifzYCcynpWTZWg","isbns":isbn})
    bookres = res.json()

    name = db.execute("SELECT title FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()[0]
    author = db.execute("SELECT author FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()[0]
    published = db.execute("SELECT year FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()[0]
            
   
    if session:
        user_id = session["user_id"]
        comment = request.form.get("comment")
        rating = request.form.get("rating")
        book_name = db.execute("SELECT title FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()[0]

        if db.execute("SELECT * FROM reviews WHERE user_id=:user_id AND book_name=:book_name", {"user_id":user_id, "book_name":book_name}).rowcount == 1:
            return "you already submitted a review for this book"

        if request.method == "POST":
            db.execute("INSERT INTO reviews (user_id,book_name , rating, comment) VALUES (:user_id,:book_name,:rating,:comment)", {"user_id":user_id,"book_name":book_name ,"rating":rating,"comment":comment})
            db.commit()

        book_comment = db.execute("SELECT comment FROM reviews WHERE book_name=:book_name",{"book_name":book_name}).fetchall()
        user_name = db.execute("SELECT username FROM users WHERE user_id=:user_id",{"user_id":user_id}).fetchone()[0]

        return render_template("book.html", book_comment=book_comment,bookres=bookres, name=name, author=author, published=published, isbn=isbn, user_name=user_name, rating=rating)
    else:
            
        return redirect(url_for("signin"))


@app.route("/api/<isbn>",methods=["get"])
def api_call(isbn):
    row = db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()

    if row is None:
        return jsonify({"error":"invalid isbn"}), 422

    return jsonify({
        "isbn":row.isbn,
        "book_name":row.title,
        "author":row.author
    })