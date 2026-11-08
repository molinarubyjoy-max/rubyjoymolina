from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
from pathlib import Path

app = Flask(__name__)

DATABASE = Path(__file__).resolve().parent / "students.db"

# IMPORTANT:
# Replace this with your classmate's actual deployed Render API URL.
CLASSMATE_API = "https://palencia-shamainejoyce.onrender.com/api/students"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# LAB 7 ENDPOINTS
@app.route("/student")
def student():
    return jsonify({
        "student_id": "2024-00096",
        "name": "Ruby Joy Molina",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


@app.route("/hello")
def hello():
    return jsonify({"message": "Hello, Joy!"})


@app.route("/campus")
def campus():
    return jsonify({
        "campus": "Main Campus",
        "school": "ISUFST-SEC Campus",
        "status": "Open"
    })


@app.route("/grade")
def grade():
    return jsonify({
        "student_id": "2024-00096",
        "grade": "Passed"
    })


@app.route("/students")
def students():
    conn = get_db_connection()
    records = conn.execute(
        "SELECT * FROM students ORDER BY id"
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in records])


@app.route("/students/<int:student_id>")
def get_student(student_id):
    conn = get_db_connection()
    record = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()
    conn.close()

    if record is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(record))


@app.route("/students/year/<int:year>")
def students_by_year(year):
    conn = get_db_connection()
    records = conn.execute(
        "SELECT * FROM students WHERE year = ?",
        (year,)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in records])


# API: GET ALL OWN RECORDS
@app.route("/api/students", methods=["GET"])
def api_get_students():
    conn = get_db_connection()

    records = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(row) for row in records])


# API: GET ONE RECORD
@app.route("/api/students/<int:record_id>", methods=["GET"])
def api_get_student(record_id):
    conn = get_db_connection()

    record = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (record_id,)
    ).fetchone()

    conn.close()

    if record is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(record))


# API: ADD RECORD
@app.route("/api/students", methods=["POST"])
def api_add_student():
    data = request.get_json(silent=True) or {}

    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).strip()
    year = data.get("year")
    section = str(data.get("section", "")).strip()

    if not all([student_id, name, program, section]) or year in (None, ""):
        return jsonify({"error": "Please complete all fields."}), 400

    try:
        year = int(year)
        if year < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a positive number."}), 400

    conn = get_db_connection()

    try:
        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, name, program, year, section))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Student ID already exists."}), 409

    conn.close()

    return jsonify({"message": "Student added successfully."}), 201


# API: UPDATE RECORD
@app.route("/api/students/<int:record_id>", methods=["PUT"])
def api_update_student(record_id):
    data = request.get_json(silent=True) or {}

    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).strip()
    year = data.get("year")
    section = str(data.get("section", "")).strip()

    if not all([student_id, name, program, section]) or year in (None, ""):
        return jsonify({"error": "Please complete all fields."}), 400

    try:
        year = int(year)
        if year < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a positive number."}), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT id FROM students WHERE id = ?",
        (record_id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found."}), 404

    try:
        conn.execute("""
            UPDATE students
            SET student_id = ?, name = ?, program = ?,
                year = ?, section = ?
            WHERE id = ?
        """, (student_id, name, program, year, section, record_id))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Student ID already exists."}), 409

    conn.close()

    return jsonify({"message": "Student updated successfully."})


# API: DELETE RECORD
@app.route("/api/students/<int:record_id>", methods=["DELETE"])
def api_delete_student(record_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student deleted successfully."})


# API: RETRIEVE CLASSMATE RECORDS
@app.route("/api/classmate-students", methods=["GET"])
def get_classmate_students():
    try:
        response = requests.get(CLASSMATE_API, timeout=20)
        response.raise_for_status()

        data = response.json()

        # Accept either a JSON list or an object containing a students list.
        if isinstance(data, dict):
            data = data.get("students", [])

        if not isinstance(data, list):
            return jsonify({"error": "Invalid classmate API response."}), 502

        return jsonify(data)

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to connect to your classmate's API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({"error": "Classmate API did not return valid JSON."}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)