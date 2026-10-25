
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# HOME PAGE
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
# ORIGINAL STUDENT API
# ==========================================
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "2024-00096",
        "name": "Ruby Joy Molina",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# GREETING API
# ==========================================
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Joy')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# CAMPUS INFORMATION API
# ==========================================
@app.route('/campus')
def campus_info():
    return jsonify({
        "campus": "Main Campus",
        "location": "Iloilo",
        "type": "ISUFST-SEC Campus",
        "status": "Open"
    })


# ==========================================
# GRADE CALCULATOR API
# ==========================================
@app.route('/grade')
def calculate_grade():
    score = request.args.get('score', type=float)

    if score is None:
        return jsonify({
            "error": "Please provide a valid score."
        }), 400

    if score < 0 or score > 100:
        return jsonify({
            "error": "Score must be between 0 and 100."
        }), 400

    if score >= 90:
        remark = "Excellent"
    elif score >= 80:
        remark = "Very Good"
    elif score >= 75:
        remark = "Passed"
    else:
        remark = "Needs Improvement"

    return jsonify({
        "score": score,
        "remark": remark
    })


# ==========================================
# ACTIVITY 7: DISPLAY ALL DATABASE STUDENTS
# ==========================================
@app.route('/students')
def get_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students ORDER BY id'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==========================================
# ACTIVITY 7: DISPLAY ONE STUDENT BY ID
# ==========================================
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ==========================================
# ADDITIONAL TASK: SEARCH BY YEAR LEVEL
# ==========================================
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    if year < 1 or year > 4:
        return jsonify({
            "error": "Year level must be between 1 and 4."
        }), 400

    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE year = ? ORDER BY id',
        (year,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


if __name__ == '__main__':
    app.run(debug=True)
