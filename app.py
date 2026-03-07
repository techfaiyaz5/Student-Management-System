from flask import Flask, request, render_template_string
import mysql.connector
import os
import time

app = Flask(__name__)

# Database connection function with wait logic
def get_db_connection():
    for i in range(10):
        try:
            conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'db'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'password'),
                database=os.getenv('DB_NAME', 'student_db')
            )
            return conn
        except:
            print("Database not ready, retrying...")
            time.sleep(3)
    return None

# Simple HTML Interface for Entry
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Management</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .form-group { margin-bottom: 15px; }
        input { padding: 8px; width: 250px; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Add New Student</h2>
    <form method="POST" action="/add">
        <div class="form-group">
            <label>Name:</label><br>
            <input type="text" name="name" required>
        </div>
        <div class="form-group">
            <label>Roll No:</label><br>
            <input type="text" name="roll_no" required>
        </div>
        <div class="form-group">
            <label>Address:</label><br>
            <input type="text" name="address" required>
        </div>
        <button type="submit">Save Student</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')
    address = request.form.get('address')

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, roll_no, address) VALUES (%s, %s, %s)", 
                       (name, roll_no, address))
        conn.commit()
        cursor.close()
        conn.close()
        return f"<h3>Success! {name} (Roll: {roll_no}) has been saved.</h3> <a href='/'>Add Another</a>"
    return "<h3>Error: Could not connect to Database.</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)