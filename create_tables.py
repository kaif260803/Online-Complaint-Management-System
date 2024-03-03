import sqlite3

def create_tables():
    conn = sqlite3.connect("online_management_system.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        address TEXT NOT NULL,  
                        phone TEXT NOT NULL, 
                        registration_number TEXT NOT NULL,
                        department TEXT NOT NULL,
                        gender TEXT DEFAULT 'male', 
                        is_admin INTEGER NOT NULL)''')

    # Create complaints table
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        complaint TEXT NOT NULL,
                        department TEXT NOT NULL,
                        assigned_admin TEXT,
                        assigned_department TEXT,
                        status INTEGER DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    # Create admins table
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        department TEXT NOT NULL)''')

    # Insert initial admin data if it doesn't exist
    admins = [("Kaif", "yes", "Computer Science and Engineering"),
              ("Sai", "yes", "Electrical Engineering"),
              ("Rohit", "yes", "Automobile Engineering"),
              ("Abhi", "yes", "Biotechnology")]
    for admin in admins:
        cursor.execute("INSERT OR IGNORE INTO admins (username, password, department) VALUES (?, ?, ?)", admin)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()

