
import sqlite3

DATABASE = "students.db"

conn = sqlite3.connect(DATABASE)

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
""")

columns = [
    row[1]
    for row in conn.execute("PRAGMA table_info(students)").fetchall()
]

if "source" not in columns:
    conn.execute("""
        ALTER TABLE students
        ADD COLUMN source TEXT DEFAULT 'Local'
    """)

conn.commit()
conn.close()

print("Database initialized successfully!")

import sqlite3

DATABASE = "students.db"

conn = sqlite3.connect(DATABASE)

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
""")

columns = [
    row[1]
    for row in conn.execute("PRAGMA table_info(students)").fetchall()
]

if "source" not in columns:
    conn.execute("""
        ALTER TABLE students
        ADD COLUMN source TEXT DEFAULT 'Local'
    """)

conn.commit()
conn.close()

print("Database initialized successfully!")
