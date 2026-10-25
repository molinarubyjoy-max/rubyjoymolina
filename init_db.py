
import sqlite3

# Connect to the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Clear previous sample records
cursor.execute('DELETE FROM students')

# Reset the automatic ID counter
cursor.execute(
    "DELETE FROM sqlite_sequence WHERE name = 'students'"
)

# Five sample student records
students = [
    ('2024-00096', 'Ruby Joy Molina', 'BSIT', 3, 'B'),
    ('2026-00124', 'Maria Santos', 'BSIT', 1, 'A'),
    ('2026-00125', 'Pedro Reyes', 'BSIT', 1, 'B'),
    ('2025-00130', 'Angela Cruz', 'BSCS', 2, 'A'),
    ('2024-00145', 'Daniel Garcia', 'BSCS', 3, 'B')
]

# Insert student records
cursor.executemany('''
INSERT INTO students (
    student_id, name, program, year, section
)
VALUES (?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
print("Five student records inserted.")
