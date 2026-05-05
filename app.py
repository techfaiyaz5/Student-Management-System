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
                    address VARCHAR(255),
                    mobile_no VARCHAR(15)
                )
            """)
            # Add mobile_no column if it doesn't exist (for existing tables)
            try:
                cursor.execute("ALTER TABLE students ADD COLUMN mobile_no VARCHAR(15)")
                conn.commit()
                print("Success: mobile_no column added!")
            except Exception as e:
                print("Info: mobile_no column already exists or skipping.")
            
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduTrack | Student Management System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg-primary: #f0f4f8;
            --bg-secondary: #e8edf3;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --border: #e2e8f0;
            --accent: #4f72d4;
            --accent2: #6c8de6;
            --accent3: #0ea5e9;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            background-image:
                radial-gradient(ellipse at 20% 10%, rgba(79,114,212,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 90%, rgba(14,165,233,0.06) 0%, transparent 50%);
        }

        /* ── Sidebar ── */
        .sidebar {
            position: fixed; top: 0; left: 0;
            width: 260px; height: 100vh;
            background: #ffffff;
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border);
            box-shadow: 2px 0 16px rgba(79,114,212,0.07);
            display: flex; flex-direction: column;
            padding: 0; z-index: 100;
        }
        .sidebar-logo {
            padding: 28px 24px 20px;
            border-bottom: 1px solid var(--border);
        }
        .logo-icon {
            width: 42px; height: 42px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px; margin-bottom: 12px;
            box-shadow: 0 4px 14px rgba(79,114,212,0.25);
        }
        .logo-text { font-size: 20px; font-weight: 800; letter-spacing: -0.5px; color: #1e293b; }
        .logo-text span { color: var(--accent); }
        .logo-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; text-transform: uppercase; letter-spacing: 1px; }

        .sidebar-nav { padding: 20px 12px; flex: 1; }
        .nav-label { font-size: 10px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; padding: 0 12px; margin-bottom: 8px; margin-top: 16px; }
        .nav-item {
            display: flex; align-items: center; gap: 12px;
            padding: 11px 14px; border-radius: 10px;
            font-size: 14px; font-weight: 500;
            color: var(--text-secondary); cursor: pointer;
            transition: all 0.2s; text-decoration: none;
            margin-bottom: 2px;
        }
        .nav-item:hover { background: #f1f5fb; color: var(--accent); }
        .nav-item.active { background: linear-gradient(135deg, rgba(79,114,212,0.12), rgba(108,141,230,0.1)); color: var(--accent); border: 1px solid rgba(79,114,212,0.2); }
        .nav-item i { width: 18px; text-align: center; font-size: 15px; }

        .sidebar-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--border);
        }
        .user-avatar {
            width: 36px; height: 36px; border-radius: 50%;
            background: linear-gradient(135deg, var(--accent3), var(--accent));
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; font-weight: 700; color: white; flex-shrink: 0;
        }
        .user-info { display: flex; align-items: center; gap: 10px; }
        .user-name { font-size: 13px; font-weight: 600; color: #1e293b; }
        .user-role { font-size: 11px; color: var(--text-muted); }

        /* ── Main Content ── */
        .main { margin-left: 260px; padding: 32px 36px; min-height: 100vh; }

        /* ── Header ── */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
        .header-left h1 { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
        .header-left p { font-size: 14px; color: var(--text-secondary); margin-top: 4px; }
        .header-right { display: flex; align-items: center; gap: 12px; }
        .badge-live {
            display: flex; align-items: center; gap: 8px;
            background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2);
            color: #059669; padding: 8px 14px; border-radius: 20px; font-size: 13px; font-weight: 500;
        }
        .dot { width: 7px; height: 7px; background: var(--success); border-radius: 50%; animation: pulse 1.8s infinite; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(1.3)} }

        /* ── Stats Cards ── */
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px; padding: 22px 24px;
            box-shadow: 0 2px 12px rgba(79,114,212,0.07);
            transition: all 0.3s; position: relative; overflow: hidden;
        }
        .stat-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        }
        .stat-card.s1::before { background: linear-gradient(90deg, var(--accent), var(--accent2)); }
        .stat-card.s2::before { background: linear-gradient(90deg, var(--success), #34d399); }
        .stat-card.s3::before { background: linear-gradient(90deg, var(--accent3), #38bdf8); }
        .stat-card:hover { background: var(--bg-card-hover); transform: translateY(-3px); box-shadow: 0 10px 28px rgba(79,114,212,0.13); }
        .stat-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
        .stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .s1 .stat-icon { background: rgba(79,114,212,0.1); color: var(--accent); }
        .s2 .stat-icon { background: rgba(16,185,129,0.1); color: var(--success); }
        .s3 .stat-icon { background: rgba(14,165,233,0.1); color: var(--accent3); }
        .stat-num { font-size: 36px; font-weight: 800; letter-spacing: -1px; color: #1e293b; }
        .stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
        .stat-badge {
            font-size: 11px; padding: 3px 8px; border-radius: 20px; font-weight: 600;
        }
        .badge-green { background: rgba(16,185,129,0.1); color: #059669; }
        .badge-blue { background: rgba(79,114,212,0.1); color: var(--accent); }
        .badge-cyan { background: rgba(14,165,233,0.1); color: #0284c7; }

        /* ── Layout Grid ── */
        .content-grid { display: grid; grid-template-columns: 1fr 380px; gap: 24px; align-items: start; }

        /* ── Form Card ── */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px; padding: 28px;
            box-shadow: 0 2px 12px rgba(79,114,212,0.07);
        }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
        .card-icon { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
        .card-icon.purple { background: rgba(99,102,241,0.15); color: var(--accent); }
        .card-icon.cyan { background: rgba(6,182,212,0.15); color: var(--accent3); }
        .card-title { font-size: 17px; font-weight: 700; }
        .card-sub { font-size: 12px; color: var(--text-muted); margin-top: 1px; }

        .form-group { margin-bottom: 16px; }
        .form-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; display: block; }
        .form-input {
            width: 100%; padding: 12px 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: all 0.2s; outline: none;
        }
        .form-input::placeholder { color: var(--text-muted); }
        .form-input:focus { border-color: var(--accent); background: #fff; box-shadow: 0 0 0 3px rgba(79,114,212,0.12); }
        .input-icon-wrap { position: relative; }
        .input-icon-wrap .form-input { padding-left: 42px; }
        .input-icon-wrap i { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 14px; }

        .btn-submit {
            width: 100%; padding: 13px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: white; border: none; border-radius: 10px;
            font-family: 'Inter', sans-serif;
            font-size: 15px; font-weight: 600; cursor: pointer;
            transition: all 0.3s; margin-top: 8px;
            box-shadow: 0 4px 14px rgba(79,114,212,0.3);
        }
        .btn-submit:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(79,114,212,0.4); }
        .btn-submit:active { transform: translateY(0); }
        .btn-submit i { margin-right: 8px; }

        /* ── Table ── */
        .table-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(79,114,212,0.07); }
        .table-head { padding: 22px 28px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .table-count { font-size: 13px; color: var(--text-muted); background: #f1f5f9; padding: 5px 12px; border-radius: 20px; }

        table { width: 100%; border-collapse: collapse; }
        thead th {
            padding: 14px 20px;
            font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
            color: var(--text-muted); text-align: left;
            background: #f8fafc;
            border-bottom: 1px solid var(--border);
        }
        tbody tr { transition: background 0.2s; border-bottom: 1px solid #f1f5f9; }
        tbody tr:hover { background: #f8fafc; }
        tbody tr:last-child { border-bottom: none; }
        tbody td { padding: 16px 20px; font-size: 14px; color: var(--text-secondary); vertical-align: middle; }

        .student-name { display: flex; align-items: center; gap: 12px; }
        .avatar {
            width: 34px; height: 34px; border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            display: flex; align-items: center; justify-content: center;
            font-size: 13px; font-weight: 700; color: white; flex-shrink: 0;
        }
        .name-text { font-weight: 600; color: var(--text-primary); font-size: 14px; }

        .roll-badge {
            background: rgba(79,114,212,0.08);
            color: var(--accent); border: 1px solid rgba(79,114,212,0.18);
            padding: 4px 10px; border-radius: 6px;
            font-size: 12px; font-weight: 600; font-family: 'Courier New', monospace;
            display: inline-block;
        }
        .mobile-text { display: flex; align-items: center; gap: 6px; color: var(--text-secondary); }
        .mobile-text i { color: var(--success); font-size: 12px; }

        .btn-delete {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 7px 14px; border-radius: 8px;
            background: rgba(239,68,68,0.1); color: #f87171;
            border: 1px solid rgba(239,68,68,0.2);
            text-decoration: none; font-size: 12px; font-weight: 600;
            transition: all 0.2s;
        }
        .btn-delete:hover { background: rgba(239,68,68,0.2); border-color: rgba(239,68,68,0.4); transform: translateY(-1px); }

        .empty-state { text-align: center; padding: 60px 20px; color: var(--text-muted); }
        .empty-state i { font-size: 48px; margin-bottom: 16px; opacity: 0.3; }
        .empty-state p { font-size: 15px; }

        /* Animations */
        @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
        .stat-card { animation: fadeUp 0.5s ease both; }
        .stat-card:nth-child(1){animation-delay:0.1s}
        .stat-card:nth-child(2){animation-delay:0.2s}
        .stat-card:nth-child(3){animation-delay:0.3s}
        .card { animation: fadeUp 0.5s 0.2s ease both; }
        .table-card { animation: fadeUp 0.5s 0.3s ease both; }

        /* Scrollbar */
        ::-webkit-scrollbar{width:6px} ::-webkit-scrollbar-track{background:transparent} ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:3px}
    </style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar">
    <div class="sidebar-logo">
        <div class="logo-icon">🎓</div>
        <div class="logo-text">Edu<span>Track</span></div>
        <div class="logo-sub">Student Management System</div>
    </div>
    <nav class="sidebar-nav">
        <div class="nav-label">Main Menu</div>
        <a class="nav-item active" href="/"><i class="fas fa-gauge-high"></i> Dashboard</a>
        <a class="nav-item" href="/"><i class="fas fa-users"></i> Students</a>
        <a class="nav-item" href="/"><i class="fas fa-user-plus"></i> Add Student</a>
        <div class="nav-label">System</div>
        <a class="nav-item" href="/"><i class="fas fa-chart-pie"></i> Analytics</a>
        <a class="nav-item" href="/"><i class="fas fa-gear"></i> Settings</a>
    </nav>
    <div class="sidebar-footer">
        <div class="user-info">
            <div class="user-avatar">A</div>
            <div>
                <div class="user-name">Admin</div>
                <div class="user-role">Super Administrator</div>
            </div>
        </div>
    </div>
</aside>

<!-- Main Content -->
<main class="main">

    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <h1>Dashboard Overview</h1>
            <p>Manage your student records with ease</p>
        </div>
        <div class="header-right">
            <div class="badge-live"><div class="dot"></div> System Online</div>
        </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
        <div class="stat-card s1">
            <div class="stat-top">
                <div class="stat-icon"><i class="fas fa-users"></i></div>
                <span class="stat-badge badge-green">Active</span>
            </div>
            <div class="stat-num">{{ students|length }}</div>
            <div class="stat-label">Total Students Enrolled</div>
        </div>
        <div class="stat-card s2">
            <div class="stat-top">
                <div class="stat-icon"><i class="fas fa-id-card"></i></div>
                <span class="stat-badge badge-blue">Records</span>
            </div>
            <div class="stat-num">{{ students|length }}</div>
            <div class="stat-label">Active Student Records</div>
        </div>
        <div class="stat-card s3">
            <div class="stat-top">
                <div class="stat-icon"><i class="fas fa-database"></i></div>
                <span class="stat-badge badge-cyan">Live</span>
            </div>
            <div class="stat-num">DB</div>
            <div class="stat-label">MySQL Database Connected</div>
        </div>
    </div>

    <!-- Content Grid -->
    <div class="content-grid">

        <!-- Student Table -->
        <div class="table-card">
            <div class="table-head">
                <div>
                    <div class="card-title" style="font-size:16px;">Student Records</div>
                    <div class="card-sub" style="font-size:12px;color:var(--text-muted);margin-top:2px;">All enrolled students</div>
                </div>
                <span class="table-count">{{ students|length }} total</span>
            </div>
            {% if students %}
            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Roll No</th>
                        <th>Address</th>
                        <th>Mobile</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                {% for student in students %}
                <tr>
                    <td>
                        <div class="student-name">
                            <div class="avatar">{{ student[0][0]|upper }}</div>
                            <span class="name-text">{{ student[0] }}</span>
                        </div>
                    </td>
                    <td><span class="roll-badge">{{ student[1] }}</span></td>
                    <td><i class="fas fa-location-dot" style="color:var(--accent);margin-right:6px;font-size:12px;"></i>{{ student[2] }}</td>
                    <td>
                        <div class="mobile-text">
                            <i class="fas fa-phone"></i>{{ student[3] }}
                        </div>
                    </td>
                    <td>
                        <a href="/delete/{{ student[1] }}" class="btn-delete" onclick="return confirm('Delete {{ student[0] }}? This cannot be undone.')">
                            <i class="fas fa-trash"></i> Delete
                        </a>
                    </td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty-state">
                <i class="fas fa-users-slash"></i>
                <p>No students enrolled yet.<br>Add your first student using the form.</p>
            </div>
            {% endif %}
        </div>

        <!-- Add Student Form -->
        <div class="card">
            <div class="card-header">
                <div class="card-icon purple"><i class="fas fa-user-plus"></i></div>
                <div>
                    <div class="card-title">Add New Student</div>
                    <div class="card-sub">Fill in student details below</div>
                </div>
            </div>
            <form method="POST" action="/add">
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <div class="input-icon-wrap">
                        <i class="fas fa-user"></i>
                        <input id="inp-name" type="text" name="name" class="form-input" placeholder="e.g. Ali Hassan" required>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Roll Number</label>
                    <div class="input-icon-wrap">
                        <i class="fas fa-hashtag"></i>
                        <input id="inp-roll" type="text" name="roll_no" class="form-input" placeholder="e.g. CS-2024-001" required>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Address</label>
                    <div class="input-icon-wrap">
                        <i class="fas fa-map-pin"></i>
                        <input id="inp-addr" type="text" name="address" class="form-input" placeholder="e.g. Lahore, Pakistan" required>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Mobile Number</label>
                    <div class="input-icon-wrap">
                        <i class="fas fa-phone"></i>
                        <input id="inp-mobile" type="tel" name="mobile_no" class="form-input" placeholder="e.g. 0300-1234567" required>
                    </div>
                </div>
                <button type="submit" class="btn-submit" id="btn-add">
                    <i class="fas fa-plus"></i> Enroll Student
                </button>
            </form>
        </div>

    </div>
</main>

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
            cursor.execute("SELECT name, roll_no, address, mobile_no FROM students")
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
    mobile_no = request.form.get('mobile_no')
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, roll_no, address, mobile_no) VALUES (%s, %s, %s, %s)", (name, roll_no, address, mobile_no))
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