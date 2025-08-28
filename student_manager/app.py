from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"   # Needed for session & flash

#Database Setup 
engine = create_engine("mysql+pymysql://root:@localhost/student")
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    usn = Column(String(255), unique=True)
    passw = Column(String(255))

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
db_session = Session()

#Authentication
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        usn = request.form["usn"].strip()
        password = request.form["password"].strip()

        # Hash password
        hashed_pw = generate_password_hash(password)

        # Save new user
        new_user = User(name=username, usn=usn, passw=hashed_pw)
        db_session.add(new_user)
        db_session.commit()

        flash("Registered successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = db_session.query(User).filter_by(name=username).first()

        if user and check_password_hash(user.passw, password):
            session["user_id"] = user.id
            session["username"] = user.name
            flash("Login successful!")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials!")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

#Student Manager
@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username")
        usn = request.form.get("usn")
        password = request.form.get("password")

        hashed_pw = generate_password_hash(password)
        new_student = User(name=username, usn=int(usn), passw=hashed_pw)
        db_session.add(new_student)
        db_session.commit()
        return redirect(url_for("home"))

    students = db_session.query(User).all()
    return render_template("index.html", students=students)


@app.route("/delete/<int:id>")
def delete_student(id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    student = db_session.query(User).filter_by(id=id).first()
    if student:
        db_session.delete(student)
        db_session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

