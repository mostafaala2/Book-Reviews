import os
import requests
from helper import login_required
from flask import Flask, session , render_template ,request , redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
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



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    username = request.form.get("username")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})

        result = rows.fetchone()
        # Ensure username exists and password is correct
        if result == None or not result[2] == request.form.get("password") :
            return render_template("error.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    session.clear()
    if request.method == "POST":
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
        {"username":request.form.get("username")}).fetchone()
        if userCheck:
                return render_template("error.html", message="username already exist")
        elif not request.form.get("password"):
                return render_template("error.html", message="must provide password")

            # Ensure confirmation wass submitted
        elif not request.form.get("confirmation"):
                return render_template("error.html", message="must confirm password")

        elif not request.form.get("password") == request.form.get("confirmation"):
                return render_template("error.html", message="passwords didn't match")

        hashedPassword = request.form.get("password")

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
        {"username":request.form.get("username"),"password":hashedPassword})

        db.commit()

        return redirect("/login")
    else:
       return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search", methods=["GET"])
@login_required
def search():
    query = "%" + request.args.get("book") + "%"
    # Capitalize all words of input for search
    query = query.title()
    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :query OR \
                        title LIKE :query OR \
                        author LIKE :query LIMIT 15",
                        {"query": query})

    if rows.rowcount == 0:
        return render_template("error.html", message="we can't find books with that description.")

    books = rows.fetchall()


    return render_template("results.html",books=books )

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
