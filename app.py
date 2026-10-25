
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# Home endpoint
@app.route('/')
def home():
    return render_template('index.html')


# Student endpoint
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "2024-00096",
        "name": "Ruby Joy Molina",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# Hello endpoint
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Joy')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# Campus Information endpoint
@app.route('/campus')
def campus_info():
    return jsonify({
        "campus": "Main Campus",
        "location": "Iloilo",
        "type": "ISUFST-SEC Campus",
        "status": "Open"
    })


# Grade Calculator endpoint
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


if __name__ == '__main__':
    app.run(debug=True)
