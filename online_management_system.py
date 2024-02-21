import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from register_dialog import RegisterDialog

class OnlineManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Management System")
        self.root.geometry("800x600")

        self.conn = sqlite3.connect("online_management_system.db")
        self.create_tables()

        self.username = None
        self.create_login_gui()

    def create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            is_admin INTEGER NOT NULL)''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS complaints (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            complaint TEXT NOT NULL,
                            department TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.conn.commit()

        admins = [("Kaif", "yes", 1, "Computer Science and Engineering"),
                  ("Sai", "yes", 1, "Electrical Engineering"),
                  ("Rohit", "yes", 1, "Automobile Engineering"),
                  ("Abhi", "yes", 1, "Biotechnology")]
        for admin in admins:
            self.conn.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)", (admin[0], "yes", admin[2]))
        self.conn.commit()

    def create_login_gui(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=20, pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor = self.conn.execute("SELECT password, is_admin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row:
            stored_password, is_admin = row
            if password == stored_password:
                self.username = username
                if is_admin:
                    self.create_admin_gui()
                else:
                    self.create_user_gui()
            else:
                messagebox.showwarning("Warning", "Incorrect password. Please try again.")
        else:
            messagebox.showwarning("Warning", "User not found. Please register.")
            RegisterDialog(self.root, self)

    def register_new_user(self, name, password, gender, address, phone, reg_num, department="Student"):
        self.conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (name, password))
        user_id = self.get_user_id(name)
        self.conn.execute("INSERT INTO complaints (user_id, complaint, department) VALUES (?, ?, ?)", (user_id, f"Address: {address}, Phone: {phone}, Registration Number: {reg_num}", department))
        self.conn.commit()
        messagebox.showinfo("Success", "User registered successfully. Please log in.")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def create_user_gui(self):
        self.login_frame.destroy()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)
        
        self.complaint_label = tk.Label(self.main_frame, text="Complaint:")
        self.complaint_label.grid(row=0, column=0, sticky="w")
        self.complaint_entry = tk.Entry(self.main_frame)
        self.complaint_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.department_label = tk.Label(self.main_frame, text="Department:")
        self.department_label.grid(row=1, column=0, sticky="w")
        self.department_combobox = ttk.Combobox(self.main_frame, values=["Computer Science and Engineering", "Electrical Engineering", "Automobile Engineering", "Biotechnology"])
        self.department_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.department_combobox.current(0)
        
        self.submit_button = tk.Button(self.main_frame, text="Submit", command=self.add_complaint)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.logout_button = tk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=3, column=0, columnspan=2, pady=10)

    def create_admin_gui(self):
        self.login_frame.destroy()
        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(padx=20, pady=20)

        self.user_label = tk.Label(self.admin_frame, text="Normal User List:")
        self.user_label.grid(row=0, column=0, sticky="w")
        self.user_listbox = tk.Listbox(self.admin_frame, height=10)
        self.user_listbox.grid(row=1, column=0, padx=10, pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self.load_user_complaints)

        self.complaint_label_admin = tk.Label(self.admin_frame, text="Complaints:")
        self.complaint_label_admin.grid(row=0, column=1, sticky="w")
        self.complaint_listbox_admin = tk.Listbox(self.admin_frame, width=50)
        self.complaint_listbox_admin.grid(row=1, column=1, padx=10, pady=5)

        self.load_normal_users()

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, column=0, columnspan=2, pady=10)

    def load_normal_users(self):
        self.user_listbox.delete(0, tk.END)
        cursor = self.conn.execute("SELECT username FROM users WHERE is_admin = 0")
        for row in cursor:
            self.user_listbox.insert(tk.END, row[0])

    def load_user_complaints(self, event):
        selected_user = self.user_listbox.get(self.user_listbox.curselection())
        self.complaint_listbox_admin.delete(0, tk.END)
        cursor = self.conn.execute("SELECT c.complaint, c.timestamp FROM complaints c JOIN users u ON c.user_id = u.id WHERE u.username = ?", (selected_user,))
        for row in cursor:
            complaint, timestamp = row
            self.complaint_listbox_admin.insert(tk.END, f"{timestamp}: {complaint}")

    def add_complaint(self):
        complaint = self.complaint_entry.get()
        department = self.department_combobox.get()
        if complaint and department:  # Check if both complaint and department are provided
            user_id = self.get_user_id(self.username)
            self.conn.execute("INSERT INTO complaints (user_id, complaint, department) VALUES (?, ?, ?)", (user_id, complaint, department))
            self.conn.commit()
            messagebox.showinfo("Success", "Complaint submitted successfully.")
            self.complaint_entry.delete(0, tk.END)
            self.load_complaints()
        else:
            messagebox.showerror("Error", "Please enter a complaint and select a department.")

    def get_user_id(self, username):
        cursor = self.conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def logout(self):
        if hasattr(self, 'admin_frame'):
            self.admin_frame.destroy()
        elif hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        self.create_login_gui()
        self.login.frame.pack(padx=20, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineManagementSystem(root)
    root.mainloop()

