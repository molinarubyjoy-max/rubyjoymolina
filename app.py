from flask import Flask, jsonify, request 
 
app = Flask(__name__) 
 
# Home endpoint 
@app.route('/') 
def home(): 
    return "Welcome to my Flask API!" 
 
 
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
    name = request.args.get('name', 'Joy ') 
 
    return jsonify({ 
        "message": f"Hello, {name}!" 
    }) 
 
 
# NEW ENDPOINT 1: Campus information 
@app.route('/campus') 
def campus_info(): 
    return jsonify({ 
        "campus": "Main Campus", 
        "location": "Iloilo", 
        "type": "ISUFST-SEC Campus", 
        "status": "Open" 
    }) 
 
 

# NEW ENDPOINT 2: Grade Calculator
@app.route('/grade')
def calculate_grade():
    score = request.args.get('score', type=float)

    if score is None:
        return jsonify({
            "score": "100"
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