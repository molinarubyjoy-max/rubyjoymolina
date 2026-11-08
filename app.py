from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
import os

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_PATH", "students.db")
PARTNER_API_URL = os.environ.get("PARTNER_API_URL", "")


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    columns = [
        column["name"]
        for column in connection.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "source" not in columns:
        connection.execute(
            "ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'"
        )

    connection.commit()
    connection.close()


def validate_student(data):
    required_fields = ["student_id", "name", "program", "year", "section"]

    for field in required_fields:
        if not data.get(field):
            return f"{field.replace('_', ' ').title()} is required."

    return None


def save_student(data, source):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(data["student_id"]).strip(),
        str(data["name"]).strip(),
        str(data["program"]).strip(),
        str(data["year"]).strip(),
        str(data["section"]).strip(),
        source
    ))

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


# READ: Get all records from your own database
@app.route("/api/students", methods=["GET"])
def get_students():
    connection = get_db_connection()
    students = connection.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return jsonify([dict(student) for student in students])


# CREATE: Add a student record
@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True) or {}

    error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    source = data.get("source", "External API")
    save_student(data, source)

    return jsonify({
        "message": "Student record added successfully!",
        "source": source
    }), 201


# READ: Get one student record
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    connection = get_db_connection()
    student = connection.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    connection.close()

    if student is None:
        return jsonify({"error": "Student not found."}), 404

    return jsonify(dict(student))


# UPDATE: Edit a student record
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}

    error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    connection = get_db_connection()
    cursor = connection.execute("""
        UPDATE students
        SET student_id = ?, name = ?, program = ?,
            year = ?, section = ?
        WHERE id = ?
    """, (
        data["student_id"],
        data["name"],
        data["program"],
        data["year"],
        data["section"],
        student_id
    ))

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student updated successfully!"})


# DELETE: Remove a student record
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    connection = get_db_connection()
    cursor = connection.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return jsonify({"message": "Student deleted successfully!"})


# GET: Retrieve records from your classmate's API
@app.route("/partner-records", methods=["GET"])
def partner_records():
    if not PARTNER_API_URL:
        return jsonify({
            "error": "Partner API URL is not configured."
        }), 400

    try:
        response = requests.get(PARTNER_API_URL, timeout=15)
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "Partner API did not return a list of records."
            }), 502

        return jsonify(records)

    except requests.RequestException as error:
        return jsonify({
            "error": f"Unable to retrieve partner records: {str(error)}"
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API returned invalid JSON."
        }), 502


# SAVE: Import a selected classmate record into your database
@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True) or {}

    error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    save_student(data, "Classmate API")

    return jsonify({
        "message": "Partner record imported successfully!",
        "source": "Classmate API"
    }), 201


# SEND: Send a practice record to your classmate's API
@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():
    data = request.get_json(silent=True) or {}

    error = validate_student(data)
    if error:
        return jsonify({"error": error}), 400

    if not PARTNER_API_URL:
        return jsonify({
            "error": "Partner API URL is not configured."
        }), 400

    data["source"] = "Partner API"

    try:
        response = requests.post(
            PARTNER_API_URL,
            json=data,
            timeout=15
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = {"message": response.text}

        if not response.ok:
            return jsonify({
                "error": "Partner API rejected the record.",
                "partner_response": partner_response
            }), response.status_code

        return jsonify({
            "message": "Record sent to partner successfully!",
            "partner_response": partner_response
        }), 200

    except requests.RequestException as error:
        return jsonify({
            "error": f"Could not send record: {str(error)}"
        }), 502


initialize_database()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )