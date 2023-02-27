import string

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# USER_TYPES (list of str): Types of user
USER_TYPES = ["Student", "Teacher"]

# SEMESTERS (list of str): All semesters
SEMESTERS = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]

# COURSES (list of str): All courses offered for the students of CSE department at SUST
COURSES = [
    "CSE 133", "CSE 134", "CSE 137", "CSE 138", "CSE 143", "CSE 150",
    "CSE 233", "CSE 234", "CSE 237", "CSE 238", "CSE 239", "CSE 240",
    "CSE 245", "CSE 250", "CSE 252", "CSE 325", "CSE 326", "CSE 329",
    "CSE 331", "CSE 332", "CSE 333", "CSE 334", "CSE 335","CSE 336",
    "CSE 345", "CSE 346", "CSE 350", "CSE 361", "CSE 362", "CSE 365",
    "CSE 366", "CSE 367", "CSE 368", "CSE 373", "CSE 374", "CSE 376",
    "CSE 426", "CSE 433", "CSE 434", "CSE 439", "CSE 440", "CSE 446",
    "CSE 450", "CSE 452", "CSE 475", "CSE 480", "CSE 482", "CSE 484",
    "EEE 109D", "EEE 110D", "EEE 111D", "EEE 112D", "EEE 201D", "EEE 202D",
    "MAT 102D", "MAT 103D", "MAT 204D", "ENG 101D", "ENG 102D", "IPE 106D",
    "IPE 108D", "PHY 103D", "PHY 202D","PHY 207D", "BUS 203D", "STA 202D", "ECO 105D"
]

SEMESTER_1 = {
    "CSE 133": ["Structured Programming Language", 3, 0, 3.0, "None"],
    "CSE 134": ["Structured Programming Language Lab", 0, 6, 3.0, "None"],
    "CSE 143": ["Discrete Mathematics", 3, 0, 3.0, "None"],
    "EEE 109D": ["Electrical Circuits", 3, 0, 3.0, "None"],
    "EEE 110D": ["Electrical Circuits Lab", 0, 3, 1.5, "None"],
    "MAT 102D": ["Matrices, Vector Analysis and Geometry", 3, 0, 3.0, "None"],
    "ENG 101D": ["Effective Communication in English", 2, 0, 2.0, "None"],
    "ENG 102D": ["Effective Communication in English Lab", 0, 2, 1.0, "None"]
}

SEMESTER_2 = {
    "CSE 137": ["Data Structure", 3, 0, 3.0, "CSE 133"],
    "CSE 138": ["Data Structure Lab", 0, 4, 2.0, "None"],
    "EEE 111D": ["Electronic Devices and Circuits", 3, 0, 3.0, "EEE 109"],
    "EEE 112D": ["Electronic Devices and Circuits Lab", 0, 3, 1.5, "None"],
    "IPE 106D": ["Engineering Graphics", 0, 3, 1.5, "None"],
    "IPE 108D": ["Workshop Practice", 0, 2, 1.0, "None"],
    "PHY 103D": ["Mechanics, Wave, Heat & Thermodynamics", 3, 0, 3.0, "None"],
    "MAT 103D": ["Calculus", 3, 0, 3.0, "None"],
    "CSE 150": ["Project Work I", 0, 2, 1.0, "None"]
}

SEMESTER_3 = {
    "CSE 233": ["Object Oriented Programming Language", 3, 0, 3.0, "CSE 133"],
    "CSE 234": ["Object Oriented Programming Language Lab", 0, 4, 2.0, "None"],
    "CSE 237": ["Algorithm Design & Analysis", 3, 0, 3.0, "CSE 137"],
    "CSE 238": ["Algorithm Design & Analysis Lab", 0, 4, 2.0, "None"],
    "BUS 203": ["Cost and Management Accounting", 3, 0, 3.0, "None"],
    "PHY 207D": ["Electromagnetism, Optics & Modern Physics", 3, 0, 3.0, "None"],
    "PHY 202D": ["Basic Physics Lab", 0, 3, 1.5, "None"],
    "STA 202D": ["Basic Statistics & Probability", 3, 0, 3.0, "None"],
}

SEMESTER_4 = {
    "EEE 201D": ["Digital Logic Design", 3, 0, 3.0, "EEE 109"],
    "EEE 202D": ["Digital Logic Design Lab", 0, 4, 2.0, "None"],
    "CSE 239": ["Numerical Analysis", 2, 0, 2.0, "None"],
    "CSE 240": ["Numerical Analysis Lab", 0, 3, 1.5, "None"],
    "CSE 245": ["Theory of Computation", 3, 0, 3.0, "None"],
    "CSE 249": ["Ethics and Cyber Law", 2, 0, 2.0, "None"],
    "CSE 252": ["Competitive Programming", 0, 3, 1.5, "None"],
    "ECO 105D": ["Principles of Economics", 3, 0, 3.0, "None"],
    "MAT 204D": ["Complex Variables, Laplace Transform and Fourier Series", 3, 0, 3.0, "None"],
    "CSE 250": ["Project Work II", 0, 2, 1.0, "None"]
}

SEMESTER_5 = {
    "CSE 333": ["Database System", 3, 0, 3.0, "CSE 333"],
    "CSE 334": ["Database System Lab", 0, 4, 2.0, "CSE 334"],
    "CSE 335": ["Operating System and System Programming", 3, 0, 3.0, "None"],
    "CSE 336": ["Operating System and System Programming Lab", 0, 3, 1.5, "None"],
    "CSE 365": ["Communication Engineering", 2, 0, 2.0, "None"],
    "CSE 366": ["Communication Engineering Lab", 0, 2, 1.0, "None"],
    "CSE 367": ["Microprocessor and Interfacing", 3, 0, 3.0, "None"],
    "CSE 368": ["Microprocessor and Interfacing Lab", 0, 3, 1.5, "None"],
    "CSE 325": ["Digital Signal Processing", 3, 0, 3.0, "None"],
    "CSE 326": ["Digital Signal Processing Lab", 0, 3, 1.5, "None"]
}

SEMESTER_6 = {
    "CSE 329": ["Computer Architecture", 3, 0, 3.0, "None"],
    "CSE 331": ["Software Engineering & Design Patterns", 3, 0, 3.0, "None"],
    "CSE 332": ["Software Engineering & Design Patterns Lab", 0, 3, 1.5, "None"],
    "CSE 345": ["Introduction to Data Science", 2, 0, 2.0, "None"],
    "CSE 346": ["Introduction to Data Science Lab", 0, 3, 1.5, "None"],
    "CSE 361": ["Computer Networking", 3, 0, 3.0, "CSE 365"],
    "CSE 362": ["Computer Networking Lab", 0, 3, 1.5, "None"],
    "CSE 373": ["Computer Graphics ", 3, 0, 3.0, "None"],
    "CSE 374": ["Computer Graphics Lab", 0, 3, 1.5, "None"],
    "CSE 376": ["Technical Writing And Presentation", 0, 4, 2.0, "None"],
    "CSE 350": ["Project Work III", 0, 4, 2.0, "None"]
}

SEMESTER_7 = {
    "CSE 433": ["Artificial Intelligence", 3, 0, 3.0, "None"],
    "CSE 434": ["Artificial Intelligence Lab", 0, 3, 1.5, "None"],
    "CSE 475": ["Machine Learning", 3, 0, 3.0, "None"],
    "CSE 426": ["Machine Learning Lab", 0, 3, 1.5, "None"],
    "CSE 446": ["Web Technologies", 0, 4, 2.0, "None"],
    "CSE/EEE (4**)": ["Option I", 3, 0, 3.0, "None"],
    "CSE/EEE (4**)": ["Option I Lab", 0, 3, 1.5, "CSE/EEE (4**)"],
    "CSE ***": ["Thesis / Project", 0, 4, 2.0, "CSE ***"]
}

SEMESTER_8 = {
    "CSE 439": ["Compiler Construction", 3, 0, 3.0, "CSE 243"],
    "CSE 440": ["Compiler Construction Lab", 0, 3, 1.5, "None"],
    "CSE/EEE (4**)": ["Option II", 3, 0, 3.0, "None"],
    "CSE/EEE (4**)": ["Option II Lab", 0, 3, 1.5, "None"],
    "CSE ***": ["Thesis / Project", 0, 8, 4.0, "None"],
    "CSE 484": ["Viva Voce", 0, 2, 1.0, "None"],
}

FACULTY = {
    "Dr Muhammed Zafar Iqbal": ["Professor (Retired)", "mzi@sust.edu"],
    "Mohammad Abdullah Al Mumin": ["Professor & Head", "mumin-cse@sust.edu"],
    "Mohammad Shahidur Rahman": ["Professor", "rahmanms@sust.edu"],
    "Dr Mohammad Reza Selim": ["Professor", "selim@sust.edu"],
    "M. Jahirul Islam": ["Professor", "jahir-cse@sust.edu"],

    "Md Masum": ["Professor", "masum-cse@sust.edu"],
    "Dr. Farida Chowdhury": ["Professor", "deeba.bd@gmail.com"],
    "Dr. Md Forhad Rabbi": ["Professor", "frabbi-cse@sust.edu"],
    "Husne Ara Chowdhury": ["Associate Professor", "husne-cse@sust.edu"],
    "Sadia Sultana": ["Associate Professor", "sadia-cse@sust.edu"],

    "Mahruba Sharmin Chowdhury": ["Assistant Professor", "ahruba-cse@sust.edu"],
    "Ayesha Tasnim": ["Assistant Professor", "tasnim-cse@sust.edu"],
    "Md Eamin Rahman": ["Assistant Professor (On Leave)", "eamin-cse@sust.edu"],
    "Md Saiful Islam": ["Assistant Professor (On Leave)", "saiful-cse@sust.edu"],
    "Sheikh Nabil Mohammad": ["Assistant Professor (On Leave)", "nabil-cse@sust.edu"],

    "Marium-E-Jannat": ["Assistant Professor (On Leave)", "jannat-cse@sust.edu"],
    "Biswapriyo Chakrabarty": ["Assistant Professor (On Leave)", "biswa-cse@sust.edu"],
    "Md Mahfuzur Rahaman": ["Assistant Professor (On Leave)", "mahfuz-cse@sust.edu"],
    "Md Mahadi Hasan Nahid": ["Assistant Professor", "nahid-cse@sust.edu"],
    "Enamul Hassan": ["Assistant Professor", "enam-cse@sust.edu"],

    "Moqsadur Rahman": ["Assistant Professor (On Leave)", "moqsad-cse@sust.edu"],
    "Summit Haque": ["Assistant Professor", "summit-cse@sust.edu"],
    "Arnab Sen Sharma": ["Lecturer", "arnab-cse@sust.edu"],
    "Maruf Ahmed Mridul": ["Lecturer", "mridul-cse@sust.edu"]
}

# STATUS (list of str): All possible viva status
STATUS = ["Running..", "Done", "Absent"]

# COURSE (str): Course which teacher will select for seeing viva schedule
COURSE = ""

# COURSE_S (str): Course selected by student to see history
COURSE_S = ""

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///scheduler.db")


@app.route("/")
def index():
    """Shows all the viva which are scheduled sorted by course in alphabetical order"""

    # Selects all the courses from courses table
    courses = db.execute("SELECT * FROM courses ORDER BY course")

    # Shows the page with all the viva
    return render_template("index.html", courses=courses)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember user type
        session["user_type"] = rows[0]["type"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/curriculum")
def undergraduate_program():
    """
    Shows the complete undergraduate program at CSE, SUST
    """
    return render_template("undergraduate_program.html", semester_1=SEMESTER_1, semester_2=SEMESTER_2, semester_3=SEMESTER_3,\
            semester_4=SEMESTER_4, semester_5=SEMESTER_5, semester_6=SEMESTER_6, semester_7=SEMESTER_7, semester_8=SEMESTER_8)


@app.route("/faculty")
def faculty():
    """
    Shows the list of faculty at CSE, SUST
    """
    return render_template("faculty.html", faculty=FACULTY)


@app.route("/course_teacher")
@login_required
def course_teacher():
    """
    Shows all the courses for which teacher has scheduled viva sorted by
    course in alphabetical order
    """

    # id (int): User's id
    id = session["user_id"]

    # Selects all the courses which are scheduled by the teacher with the id sorted by course in
    # alphabetical order
    courses = db.execute("SELECT * FROM courses WHERE user_id = ? ORDER BY course", id)

    # Shows the page of viva which are scheduled by teacher
    return render_template("teacher.html", courses=courses)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create scheduled viva"""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure semester was submitted
        semester = request.form.get("semester")

        if not semester:
            return apology("Missing semester")

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # Ensure date was submitted
        date = request.form.get("date")

        if not date:
            return apology("Missing date")

        # Ensure time was submitted
        time = request.form.get("time")

        print("\n\n", time, "\n\n")

        if not time:
            return apology("Missing time")

        # Selects user name from users table
        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        # Checks if the user has already registered for the course or not.
        # If user has already registered return an apology
        row1 = db.execute("SELECT * FROM courses WHERE course = ?", course)

        if len(row1) > 0:
            return apology("Viva is already scheduled for this course.")

        # Inserts user id, name, semester, course, viva date and time in the courses table
        db.execute("INSERT INTO courses (user_id, name, semester, course, date, time) VALUES(?, ?, ?, ?, ?, ?)", id, name, semester, course, date, time)

        # Redirect user to the page where all the courses scheduled by user is present
        return redirect("/course_teacher")

    # Shows a form for creating viva
    return render_template("create.html", semesters=SEMESTERS, courses=COURSES)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete scheduled viva"""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # Delete course from courses table which the teacher submitted
        db.execute("DELETE FROM courses WHERE user_id = ? AND course = ?", id, course)

        # Delete all registrants from the course from regitrants table
        db.execute("DELETE FROM registrants WHERE course = ?", course)

        # Delete all registrants from history table
        db.execute("DELETE FROM history WHERE course = ?", course)

        # Redirect user to the page where all the courses scheduled by user is present
        return redirect("/course_teacher")

    # scheduled_courses (list): All the courses which are scheduled
    # by the teacher
    scheduled_courses = []

    # Selects all the courses which are scheduled by user sorted by alphabetical
    # order of course
    row = db.execute("SELECT course FROM courses WHERE user_id = ? ORDER BY course", id)

    # Insert all the courses in the list
    for element in row:
        scheduled_courses.append(element["course"])

    # Shows a form to delete course
    return render_template("delete.html", scheduled_courses=scheduled_courses)


@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    """Shows schedule for viva"""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # COURSE -> global variable
        global COURSE
        COURSE = course

        # Redirects to the page where all the schedule is for the course
        return redirect("/schedule_calender")

    # Selects everyting from courses table sorted by course in alphabetical order
    courses = db.execute("SELECT * FROM courses WHERE user_id = ? ORDER BY course", id)

    # Shows the form from where user can select course to see schedule
    return render_template("course.html", courses=courses)


@app.route("/schedule_calender", methods=["GET", "POST"])
@login_required
def schedule_calender():
    """Keep track of viva"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensures status was submitted
        status = request.form.get("status")

        if not status:
            status = "pending.."

        # Collects name and course from form
        name = request.form.get("name")
        course = request.form.get("course")

        # now (datetime): Current date and time
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        date_time = str(date_time)

        # Update status in history table
        db.execute("UPDATE history SET status = ?, datetime = ? WHERE username = ? AND course = ?", status, date_time, name, course)

        # Redirects to the page where all the schedule is for the course
        return redirect("/schedule_calender")

    # Selects everyting from history table for the course sorted by students username
    registrants = db.execute("SELECT * FROM history WHERE course = ? ORDER BY username", COURSE)

    # Shows the page where all the schedule is present
    return render_template("schedule.html", registrants=registrants, status=STATUS)


@app.route("/taken_courses")
@login_required
def taken_courses():
    """
    Displays all the courses a student has taken.
    """

    # id (int): User's id who are of type student
    id = session["user_id"]

    # Selects all the courses a student has registered
    courses = db.execute("SELECT * FROM registrants WHERE user_id = ? ORDER BY course", id)

    # Shows the page with all the courses taken by student
    return render_template("taken_courses.html", courses=courses)


@app.route("/course_register", methods=["GET", "POST"])
@login_required
def course_register():
    """ Register students for course."""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # Select all the available courses scheduled for viva
        row = db.execute("SELECT * FROM courses WHERE course = ?", course)

        # Collects teacher's name
        teacher = row[0]["name"]

        # Checks if the user has already registered for the course or not
        # If user has already registered return an apology
        row1 = db.execute("SELECT * FROM registrants WHERE user_id = ? AND course = ? AND teacher = ?", id, course, teacher)

        if len(row1) > 0:
            return apology("You have already registered for this course!")

        # Inserts user id, teacher and course into the registrants table
        db.execute("INSERT INTO registrants (user_id, teacher, course) VALUES(?, ?, ?)", id, teacher, course)

        # Collects student's name
        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        # Inserts student's username and coure into history table
        db.execute("INSERT INTO history (username, course) VALUES(?, ?)", name, course)

        # Redirects the user to the page where all of the taken courses are present
        return redirect("/taken_courses")

    # Selects all the available courses for viva
    courses = db.execute("SELECT * FROM courses ORDER BY course")

    # Shows the registration form for the viva
    return render_template("course_register.html", courses=courses)


@app.route("/course_deregister", methods=["GET", "POST"])
@login_required
def course_deregister():
    """Deregister from course"""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # Collects student's username
        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        # Delete student from the course in history table
        db.execute("DELETE FROM history WHERE username = ? AND course = ?", name, course)

        # Delete user from the course in the registrants table
        db.execute("DELETE FROM registrants WHERE user_id = ? AND course = ?", id, course)

        # Redirect user to the page where all of user's taken courses are present
        return redirect("/taken_courses")

    # Selects all the courses the user has already registered
    courses = db.execute("SELECT * FROM registrants WHERE user_id = ? ORDER BY course", id)

    # Show the form for deregistration from course
    return render_template("deregister.html", courses=courses)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Shows the form selecting course to see history"""

    # id (int): User's id
    id = session["user_id"]

    # User reached route via post (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure course was submitted
        course = request.form.get("course")

        if not course:
            return apology("Missing course")

        # COURSE_S -> global variable
        global COURSE_S
        COURSE_S = course

        # Redirects the user to the page where all the history for the course is present
        return redirect("/history_calender")

    # Selects all the courses the user has registered
    courses = db.execute("SELECT course FROM registrants WHERE user_id = ? ORDER BY course", id)

    # Shows the form for sumbitting course to see history
    return render_template("history.html", courses=courses)


@app.route("/history_calender")
@login_required
def history_calender():
    """
    Shows the history of viva to student
    """

    # Selects everyting from history table for the course
    registrants = db.execute("SELECT * FROM history WHERE course = ? ORDER BY username", COURSE_S)

    # Show the history of the course
    return render_template("summary.html", registrants=registrants)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (As by submitting a form via POST)
    if request.method == "POST":

        # Ensure user type was submitted
        user_type = request.form.get("type")

        if not user_type:
            return apology("Must select user type")

        # Ensure user name was submitted
        username = request.form.get("username")

        if not username:
            return apology("MUST PROVIDE USERNAME!")

        # Ensure username doesn't exist already
        row = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(row) > 0:
            return apology("USERNAME ALREADY EXIST!")

        # Get users password and confirmation from form
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure password and confirmation was provided
        if not password or not confirmation:
            return apology("MUST PROVIDE PASSWORD!")

        # Ensure password and confirmation are same
        if password != confirmation:
            return apology("PASSWORD DOESN'T MATCH!")

        # Checking valid password
        digits = "0123456789"
        punctuations = string.punctuation
        letters = string.ascii_lowercase + string.ascii_uppercase

        digit_present = False
        punctuation_present = False
        letter_present = False

        # Checking if password contain letter, digit, symbol or not
        for char in password:
            if char in digits:
                digit_present = True
            elif char in punctuations:
                punctuation_present = True
            elif char in letters:
                letter_present = True

        # If length of password is less than 5 or it doesn't contain letter, digit
        # and punctuation then reject registration
        if len(password) < 5 or not digit_present or not punctuation_present or not letter_present:
            return apology("Length of password must be atleast 5 and it should contain letter, digit and symbol")

        # Generates hash value of password
        password_hash = generate_password_hash(password)

        # Inserts user in the users table
        db.execute("INSERT INTO users (type, username, hash) VALUES(?, ?, ?)", user_type, username, password_hash)

        # Redirect user to login form
        return redirect("/login")

    # User reached route via GET (As by clicking a link or via redirect)
    return render_template("register.html", user_types=USER_TYPES)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
