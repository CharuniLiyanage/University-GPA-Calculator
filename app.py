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
    # Users table
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

# Clean up any NULL usernames (optional safety)
def cleanup_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET username='user'||id WHERE username IS NULL OR username=''")
    conn.commit()
    conn.close()

# Initialize DB
create_tables()
cleanup_users()

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

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 1️⃣ Validation
        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_FILE, timeout=10) as conn:
                cursor = conn.cursor()

                # 2️⃣ Check email first
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    flash("This email is already registered. Please login.", "warning")
                    return redirect(url_for('login'))

                # 3️⃣ Check username too
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    flash("Username already exists. Choose a different one.", "warning")
                    return redirect(url_for('register'))

                # 4️⃣ Insert user
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, hashed_password)
                )
                conn.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            # backup in case UNIQUE constraint is triggered
            flash("Email or Username already exists. Please login.", "warning")
            return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- LOGIN ----------------
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

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    rows = db.execute(
        "SELECT id, subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    subjects_list = [dict(row) for row in rows]

    user_data = db.execute("SELECT gpa FROM users WHERE id=?", (session["user_id"],)).fetchone()
    calculated_gpa, _, _ = calculate_gpa(subjects_list)
    db.close()

    display_gpa = user_data["gpa"] if user_data and user_data["gpa"] > 0 else calculated_gpa

    return render_template(
        "dashboard.html",
        username=session["username"],
        subjects=subjects_list,
        gpa=display_gpa
    )

# ---------------- ADD SUBJECT ----------------
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

# ---------------- GPA CALCULATOR ----------------
@app.route("/gpa_calculator", methods=["GET", "POST"])
def gpa_calculator_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    rows = db.execute(
        "SELECT id, subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    subjects_list = [dict(row) for row in rows]

    gpa, total_credits, weak_count = calculate_gpa(subjects_list)

    if request.method == "POST":
        db.execute("UPDATE users SET gpa=? WHERE id=?", (gpa, session["user_id"]))
        db.commit()
        db.close()
        flash(f"GPA saved: {gpa}", "success")
        return redirect(url_for("gpa_calculator_route"))

    db.close()
    return render_template("gpa_calculator.html", gpa=gpa, subjects=subjects_list)

# ---------------- DELETE SUBJECT ----------------
@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM subjects WHERE id=? AND user_id=?", (subject_id, session["user_id"]))
    db.commit()
    db.close()

    flash("Subject removed.", "info")
    return redirect(url_for("gpa_calculator_route"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student_dashboard")
def student_dashboard():
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    db = get_db()
    subjects = db.execute(
        "SELECT subject_name, credit, grade FROM subjects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    user = db.execute("SELECT gpa FROM users WHERE id=?", (session["user_id"],)).fetchone()
    db.close()

    gpa = user["gpa"] if user else 0

    return render_template(
        "student_dashboard.html",
        subjects=[dict(s) for s in subjects],
        gpa=gpa
    )

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
