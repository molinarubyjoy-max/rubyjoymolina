import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "students.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

cursor.execute("SELECT COUNT(*) FROM students")
count = cursor.fetchone()[0]

if count == 0:
    sample_students = [
        ("2024-00096", "Ruby Joy Molina", "BSIT", 3, "B"),
        ("2026-00124", "Maria Santos", "BSIT", 1, "A"),
        ("2026-00125", "Pedro Reyes", "BSIT", 1, "B"),
        ("2025-00130", "Angela Cruz", "BSCS", 2, "A"),
        ("2024-00145", "Daniel Garcia", "BSCS", 3, "B"),
        ("2026-00150", "John Michael Reyes", "BSIT", 1, "C"),
        ("2026-00151", "Jane Marie Cruz", "BSCS", 2, "B")
    ]

    cursor.executemany("""
        INSERT INTO students
        (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)
    """, sample_students)

    conn.commit()
    print("Seven sample student records inserted successfully.")

else:
    print("Existing student records found. No sample records inserted again.")

conn.close()

print("Database initialized successfully.")