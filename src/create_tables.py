import sqlite3

def create_tables():
    conn = sqlite3.connect("online_management_system.db")
    cursor = conn.cursor()

    # Create departments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS departments (
                   dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   dept_name TEXT NOT NULL UNIQUE)''')

    # Insert initial departments data if it doesn't exist
    departments = [("Computer Science and Engineering",),
                   ("Electrical Engineering",),
                   ("Automobile Engineering",),
                   ("Civil Engineering",),
                   ("Mechanical Engineering",),
                   ("Biotechnology",)]

    for department in departments:
        cursor.execute("INSERT OR IGNORE INTO departments (dept_name) VALUES (?)", department)

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        address TEXT NOT NULL,  
                        phone TEXT NOT NULL, 
                        registration_number TEXT NOT NULL,
                        department TEXT NOT NULL,
                        dept_id INTEGER,
                        gender TEXT DEFAULT 'male', 
                        is_admin INTEGER NOT NULL,
                        FOREIGN KEY (dept_id) REFERENCES departments(id))''')


    # Create complaints table
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        complaint TEXT NOT NULL,
                        dept_id INTEGER,
                        department TEXT NOT NULL,
                        assigned_admin TEXT,
                        assigned_department TEXT,
                        status INTEGER DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (dept_id) REFERENCES departments(id),
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    # Create admins table
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        is_admin INTEGER NOT NULL,
                        dept_id INTEGER,
                        department TEXT NOT NULL,
                        FOREIGN KEY (dept_id) REFERENCES departments(id))''')

    # Insert initial admin data if it doesn't exist
    admins = [("Kaif", "kaif", "Computer Science and Engineering"),
              ("Sai", "sai", "Electrical Engineering"),
              ("Rohit", "rohit", "Automobile Engineering"),
              ("Abhi", "abhi", "Biotechnology")]
    for admin in admins:
        cursor.execute("INSERT OR IGNORE INTO admins (username, password, department, is_admin) VALUES (?, ?, ?, 1)", admin)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()

