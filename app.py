from flask import Flask, request, render_template_string
import mysql.connector
import os
import time

app = Flask(__name__)

# --- AUTOMATION: Database Initialization Function ---
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Table banao agar nahi hai
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    roll_no VARCHAR(50),
                    address VARCHAR(255)
                )
            """)
            
            # 2. ✅ SMART FIX: Existing table par UNIQUE constraint add karo
            try:
                # Isse search aur delete fast ho jayega aur locks nahi fasenge
                cursor.execute("ALTER TABLE students ADD UNIQUE (roll_no)")
                conn.commit()
                print("Success: UNIQUE constraint added to roll_no!")
            except Exception as e:
                # Agar pehle se unique hai toh MySQL error dega, use ignore karo
                print("Info: UNIQUE constraint already exists or skipping.")

            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

# Database connection function with retry logic
def get_db_connection():
    db_host = os.getenv('DB_HOST', 'db-service')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_name = os.getenv('DB_NAME', 'student_db')

    for i in range(10):
        try:
            conn = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            return conn
        except:
            print(f"Attempt {i+1}: Database not ready, retrying in 2 seconds...")
            time.sleep(2)
    return None

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System version2</title>
    <style>
        body { font-family: Arial; margin: 30px; background-color: #f4f4f4; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #007bff; color: white; }
        input { padding: 8px; margin: 5px; width: 200px; }
        button { padding: 10px 15px; background: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; }
        .btn-delete { background: #dc3545; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; }
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
                    <a href="/delete/{{ student[1] }}" class="btn-delete" onclick="return confirm('Kya aap sach mein delete karna chahte hain?')">Delete</a>
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
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, roll_no, address FROM students")
            students_list = cursor.fetchall()
        finally:
            if conn:
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
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, roll_no, address) VALUES (%s, %s, %s)", (name, roll_no, address))
            conn.commit()
        except Exception as e:
            print(f"Add Error: {e}")
            if conn: conn.rollback()
        finally:
            if conn:
                cursor.close()
                conn.close()
    return "<script>window.location.href='/';</script>"

@app.route('/delete/<roll_no>')
def delete_student(roll_no):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
            conn.commit()
            print(f"Deleted roll_no: {roll_no}")
        except Exception as e:
            print(f"Delete Error: {e}")
            if conn: conn.rollback()
            return f"Error: {str(e)}", 500
        finally:
            if conn:
                cursor.close()
                conn.close()
    return "<script>window.location.href='/';</script>"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)