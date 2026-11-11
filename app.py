
from flask import Flask, render_template, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

DATABASE = "students.db"

# PARTNER API
PARTNER_API = "https://palencia-shamainejoyce.onrender.com/api/students"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================
# GET ALL LOCAL STUDENTS
# =====================================

@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# =====================================
# ADD STUDENT / RECEIVE EXTERNAL DATA
# =====================================

@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        year = int(data["year"])

        conn = get_db_connection()

        source = data.get("source", "External API")

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            source
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student added successfully",
            "source": source
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# UPDATE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()

        result = conn.execute("""
            UPDATE students
            SET student_id=?, name=?, program=?,
                year=?, section=?
            WHERE id=?
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            int(data["year"]),
            data["section"],
            id
        ))

        conn.commit()
        conn.close()

        if result.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# DELETE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    conn = get_db_connection()

    result = conn.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


# =====================================
# RETRIEVE PARTNER RECORDS
# =====================================

@app.route("/partner-records")
def partner_records():

    try:
        response = requests.get(
            PARTNER_API,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            data = data.get("students", data.get("data", []))

        if not isinstance(data, list):
            return jsonify({
                "error": "Unexpected partner API response"
            }), 502

        return jsonify(data)

    except requests.RequestException as e:

        return jsonify({
            "error": "Unable to retrieve partner data",
            "details": str(e)
        }), 502

    except ValueError:

        return jsonify({
            "error": "Partner API returned invalid JSON"
        }), 502


# =====================================
# IMPORT PARTNER RECORD
# =====================================

@app.route("/import-student", methods=["POST"])
def import_student():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            int(data["year"]),
            data["section"],
            "Classmate API"
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Remote record saved successfully!",
            "source": "Classmate API"
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# SEND RECORD TO PARTNER
# =====================================

@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():

    record = {
        "student_id": "EXT-001",
        "name": "Sample Exchange Record",
        "program": "BSIT",
        "year": 1,
        "section": "A",
        "source": "Partner API"
    }

    try:

        response = requests.post(
            PARTNER_API,
            json=record,
            timeout=15
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = response.text

        return jsonify({
            "message": "Partner API response received",
            "status_code": response.status_code,
            "partner_response": partner_response
        }), response.status_code

    except requests.RequestException as e:

        return jsonify({
            "error": "Unable to send record",
            "details": str(e)
        }), 502


# =====================================
# INTEGRATION DASHBOARD
# =====================================

@app.route("/dashboard-data")
def dashboard_data():

    conn = get_db_connection()

    local = conn.execute("""
        SELECT * FROM students
        WHERE source = 'Local'
    """).fetchall()

    imported = conn.execute("""
        SELECT * FROM students
        WHERE source = 'Classmate API'
    """).fetchall()

    external = conn.execute("""
        SELECT * FROM students
        WHERE source NOT IN ('Local', 'Classmate API')
    """).fetchall()

    conn.close()

    return jsonify({
        "local": [dict(row) for row in local],
        "imported": [dict(row) for row in imported],
        "external": [dict(row) for row in external]
    })


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

DATABASE = "students.db"

# PARTNER API
PARTNER_API = "https://palencia-shamainejoyce.onrender.com/api/students"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================
# GET ALL LOCAL STUDENTS
# =====================================

@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# =====================================
# ADD STUDENT / RECEIVE EXTERNAL DATA
# =====================================

@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        year = int(data["year"])

        conn = get_db_connection()

        source = data.get("source", "External API")

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            source
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student added successfully",
            "source": source
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# UPDATE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()

        result = conn.execute("""
            UPDATE students
            SET student_id=?, name=?, program=?,
                year=?, section=?
            WHERE id=?
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            int(data["year"]),
            data["section"],
            id
        ))

        conn.commit()
        conn.close()

        if result.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# DELETE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    conn = get_db_connection()

    result = conn.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


# =====================================
# RETRIEVE PARTNER RECORDS
# =====================================

@app.route("/partner-records")
def partner_records():

    try:
        response = requests.get(
            PARTNER_API,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            data = data.get("students", data.get("data", []))

        if not isinstance(data, list):
            return jsonify({
                "error": "Unexpected partner API response"
            }), 502

        return jsonify(data)

    except requests.RequestException as e:

        return jsonify({
            "error": "Unable to retrieve partner data",
            "details": str(e)
        }), 502

    except ValueError:

        return jsonify({
            "error": "Partner API returned invalid JSON"
        }), 502


# =====================================
# IMPORT PARTNER RECORD
# =====================================

@app.route("/import-student", methods=["POST"])
def import_student():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    required = [
        "student_id", "name", "program",
        "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            int(data["year"]),
            data["section"],
            "Classmate API"
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Remote record saved successfully!",
            "source": "Classmate API"
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid year"}), 400


# =====================================
# SEND RECORD TO PARTNER
# =====================================

@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():

    record = {
        "student_id": "EXT-001",
        "name": "Sample Exchange Record",
        "program": "BSIT",
        "year": 1,
        "section": "A",
        "source": "Partner API"
    }

    try:

        response = requests.post(
            PARTNER_API,
            json=record,
            timeout=15
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = response.text

        return jsonify({
            "message": "Partner API response received",
            "status_code": response.status_code,
            "partner_response": partner_response
        }), response.status_code

    except requests.RequestException as e:

        return jsonify({
            "error": "Unable to send record",
            "details": str(e)
        }), 502


# =====================================
# INTEGRATION DASHBOARD
# =====================================

@app.route("/dashboard-data")
def dashboard_data():

    conn = get_db_connection()

    local = conn.execute("""
        SELECT * FROM students
        WHERE source = 'Local'
    """).fetchall()

    imported = conn.execute("""
        SELECT * FROM students
        WHERE source = 'Classmate API'
    """).fetchall()

    external = conn.execute("""
        SELECT * FROM students
        WHERE source NOT IN ('Local', 'Classmate API')
    """).fetchall()

    conn.close()

    return jsonify({
        "local": [dict(row) for row in local],
        "imported": [dict(row) for row in imported],
        "external": [dict(row) for row in external]
    })


if __name__ == "__main__":
    app.run(debug=True)
