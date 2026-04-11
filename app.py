from flask import Flask, request, render_template_string
import mysql.connector
import os
import time

app = Flask(__name__)

# Database connection function with retry logic
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
            print("Database not ready, retrying in 2 seconds...")
            time.sleep(2)
    return None

# Updated HTML Template with Action Column and Delete Button
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System</title>
    <style>
        body { font-family: Arial; margin: 30px; background-color: #f4f4f4; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #007bff; color: white; }
        input { padding: 8px; margin: 5px; width: 200px; }
        button { padding: 10px 15px; background: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; }
        .btn-delete { 
            background: #dc3545; 
            color: white; 
            padding: 6px 12px; 
            text-decoration: none; 
            border-radius: 4px; 
            font-size: 13px;
        }
        .btn-delete:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Add New Student</h2>
        <form method="POST" action="/add">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="text" name="roll_no" placeholder="Roll Number" required>
            <input type="text" name="address" placeholder="Address" required>
            <button type="submit">Add Student</button>
        </form>

        <hr>

        <h2>Stored Student Records</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Roll No</th>
                <th>Address</th>
                <th>Action</th>
            </tr>
            {% for student in students %}
            <tr>
                <td>{{ student[0] }}</td>
                <td>{{ student[1] }}</td>
                <td>{{ student[2] }}</td>
                <td>
                    <a href="/delete/{{ student[1] }}" class="btn-delete" onclick="return confirm('Kya aap sach mein is record ko delete karna chahte hain?')">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    conn = get_db_connection()
    students_list = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, roll_no, address FROM students")
        students_list = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template_string(HTML_PAGE, students=students_list)

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
    
    return "<script>window.location.href='/';</script>"

# --- NEW DELETE ROUTE ---
@app.route('/delete/<roll_no>')
def delete_student(roll_no):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # SQL Query to delete based on roll number
        cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
        conn.commit()
        cursor.close()
        conn.close()
    
    # Page ko refresh karne ke liye redirect
    return "<script>window.location.href='/';</script>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)