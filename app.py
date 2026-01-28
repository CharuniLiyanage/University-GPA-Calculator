from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_GPA2026_KEY", "GPA_dev_key")
DB_FILE = "database.db"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    db = get_db()
    cur = db.cursor()
    # Users table with GPA column
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gpa REAL DEFAULT 0
        )
    """)
    # Subjects table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            credit REAL NOT NULL,
            grade TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()

# Initialize DB
create_tables()

import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Add 'gpa' column if it doesn't exist
try:
    cur.execute("ALTER TABLE users ADD COLUMN gpa REAL DEFAULT 0")
    print("Column 'gpa' added successfully!")
except sqlite3.OperationalError as e:
    print("Probably column already exists:", e)

conn.commit()
conn.close()


# ---------------- GPA CALCULATION ----------------
def calculate_gpa(subjects):
    grade_points = {
        "A+":4.0, "A":4.0, "A-":3.7,
        "B+":3.3, "B":3.0, "B-":2.7,
        "C+":2.3, "C":2.0,
        "D":1.0, "F":0.0
    }
    total_points = 0
    total_credits = 0
    weak_count = 0

    for s in subjects:
        credit = float(s["credit"])
        gp = grade_points.get(s["grade"], 0)
        total_points += gp * credit
        total_credits += credit
        if s["grade"] in ["D", "F"]:
            weak_count += 1

    gpa = round(total_points / total_credits, 2) if total_credits else 0
    return gpa, total_credits, weak_count

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "error")
        finally:
            db.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome {user['username']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    
    # 1. Fetch subjects for the chart and table
    rows = db.execute(
        "SELECT id, subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    subjects_list = [dict(row) for row in rows]
    
    # 2. Fetch the SAVED gpa from the users table
    user_data = db.execute("SELECT gpa FROM users WHERE id=?", (session["user_id"],)).fetchone()
    
    # 3. Calculate the live gpa (in case they haven't saved it yet)
    calculated_gpa, _, _ = calculate_gpa(subjects_list)
    
    db.close()

    # Use the saved GPA, but if it's 0 and there are subjects, show the calculated one
    display_gpa = user_data["gpa"] if user_data and user_data["gpa"] > 0 else calculated_gpa

    return render_template(
        "dashboard.html",
        username=session["username"],
        subjects=subjects_list,
        gpa=display_gpa  # This matches {{ gpa }} in your HTML
    )

@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        subject_name = request.form["subject_name"]
        credit = request.form["credit"]
        grade = request.form["grade"]

        try:
            credit = float(credit)
            if credit < 1 or credit > 5:
                flash("Credit must be between 1 and 5.", "error")
                return redirect(url_for("add_subject"))
        except ValueError:
            flash("Invalid credit value.", "error")
            return redirect(url_for("add_subject"))

        db = get_db()
        db.execute(
            "INSERT INTO subjects (user_id, subject_name, credit, grade) VALUES (?, ?, ?, ?)",
            (session["user_id"], subject_name, credit, grade)
        )
        db.commit()
        db.close()

        flash(f"Subject '{subject_name}' added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_subject.html")

@app.route("/gpa_calculator", methods=["GET", "POST"])
def gpa_calculator_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    
    # 1. Fetch current subjects so the student can see/remove them
    rows = db.execute(
        "SELECT id, subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    subjects_list = [dict(row) for row in rows]

    # 2. Calculate the current GPA
    gpa, total_credits, weak_count = calculate_gpa(subjects_list)

    if request.method == "POST":
        db.execute("UPDATE users SET gpa=? WHERE id=?", (gpa, session["user_id"]))
        db.commit()
        db.close()
        flash(f"GPA saved: {gpa}", "success")
        return redirect(url_for("gpa_calculator_route"))

    db.close()
    return render_template("gpa_calculator.html", gpa=gpa, subjects=subjects_list)

@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    # Ensure the subject belongs to the logged-in user for security
    db.execute("DELETE FROM subjects WHERE id=? AND user_id=?", (subject_id, session["user_id"]))
    db.commit()
    db.close()
    
    flash("Subject removed.", "info")
    return redirect(url_for("gpa_calculator_route"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/student_dashboard")
def student_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    db = get_db()
    # Fetch all subjects for the user
    subjects = db.execute(
        "SELECT subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    # Fetch GPA
    user = db.execute(
        "SELECT gpa FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()
    db.close()

    gpa = user["gpa"] if user else 0

    return render_template(
        "student_dashboard.html",
        subjects=[dict(s) for s in subjects],  # convert Row objects to dicts
        gpa=gpa
    )


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
