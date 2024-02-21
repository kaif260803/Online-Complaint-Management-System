import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class OnlineManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Management System")
        self.root.geometry("800x600")  # Set window size

        # Create a database connection
        self.conn = sqlite3.connect("online_management_system.db")
        self.create_tables()

        self.username = None  # Variable to store current user's username

        self.create_login_gui()

    def create_tables(self):
        # Create users table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            is_admin INTEGER NOT NULL)''')

        # Create complaints table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS complaints (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            complaint TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.conn.commit()

        # Create admin users if they don't exist
        admins = [("Kaif", "yes", 1),
                  ("Sai", "yes", 1),
                  ("Rohit", "yes", 1),
                  ("Abhi", "yes", 1)]
        for admin in admins:
            self.conn.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)", admin)
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

        cursor = self.conn.execute("SELECT is_admin FROM users WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        if row:
            is_admin = row[0]
            self.username = username
            if is_admin:
                self.create_admin_gui()
            else:
                self.create_user_gui()
        else:
            # If user not found, prompt for registration
            messagebox.showwarning("Warning", "User not found. Please register.")
            RegisterDialog(self.root, self)

    def register_new_user(self, name, password, address, phone, reg_num):
        self.conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (name, password))
        user_id = self.get_user_id(name)
        self.conn.execute("INSERT INTO complaints (user_id, complaint) VALUES (?, ?)", (user_id, f"Address: {address}, Phone: {phone}, Registration Number: {reg_num}"))
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

        self.submit_button = tk.Button(self.main_frame, text="Submit", command=self.add_complaint)
        self.submit_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.logout_button = tk.Button(self.main_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_admin_gui(self):
        self.login_frame.destroy()

        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(padx=20, pady=20)

        self.complaint_label_admin = tk.Label(self.admin_frame, text="Complaints:")
        self.complaint_label_admin.grid(row=0, column=0, sticky="w")
        self.complaint_listbox_admin = tk.Listbox(self.admin_frame, width=50)
        self.complaint_listbox_admin.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.load_complaints()

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, column=0, columnspan=2, pady=10)

    def load_complaints(self):
        self.complaint_listbox_admin.delete(0, tk.END)
        cursor = self.conn.execute("SELECT c.complaint, c.timestamp, u.username FROM complaints c JOIN users u ON c.user_id = u.id")
        for row in cursor:
            complaint, timestamp, username = row
            self.complaint_listbox_admin.insert(tk.END, f"{username} - {timestamp}: {complaint}")

    def add_complaint(self):
        complaint = self.complaint_entry.get()

        if complaint:
            user_id = self.get_user_id(self.username)
            self.conn.execute("INSERT INTO complaints (user_id, complaint) VALUES (?, ?)", (user_id, complaint))
            self.conn.commit()
            messagebox.showinfo("Success", "Complaint submitted successfully.")
            self.complaint_entry.delete(0, tk.END)
            self.load_complaints()
        else:
            messagebox.showerror("Error", "Please enter a complaint.")

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

class RegisterDialog:
    def __init__(self, parent, system):
        self.parent = parent
        self.system = system
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Register New Account")

        self.name_label = tk.Label(self.dialog, text="Name:")
        self.name_label.grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self.dialog)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.password_label = tk.Label(self.dialog, text="Password:")
        self.password_label.grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.dialog, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.address_label = tk.Label(self.dialog, text="Address:")
        self.address_label.grid(row=2, column=0, sticky="w")
        self.address_entry = tk.Entry(self.dialog)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5)

        self.phone_label = tk.Label(self.dialog, text="Mobile Number:")
        self.phone_label.grid(row=3, column=0, sticky="w")
        self.phone_entry = tk.Entry(self.dialog)
        self.phone_entry.grid(row=3, column=1, padx=10, pady=5)

        self.reg_num_label = tk.Label(self.dialog, text="Registration Number:")
        self.reg_num_label.grid(row=4, column=0, sticky="w")
        self.reg_num_entry = tk.Entry(self.dialog)
        self.reg_num_entry.grid(row=4, column=1, padx=10, pady=5)

        self.register_button = tk.Button(self.dialog, text="Register", command=self.register_user)
        self.register_button.grid(row=5, column=0, columnspan=2, pady=10)

    def register_user(self):
        name = self.name_entry.get()
        password = self.password_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        reg_num = self.reg_num_entry.get()

        if name and password and address and phone and reg_num:
            self.system.register_new_user(name, password, address, phone, reg_num)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineManagementSystem(root)
    root.mainloop()

