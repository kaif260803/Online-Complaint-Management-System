import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from user_gui import UserGUI
from admin_gui import AdminGUI
from register_dialog import RegisterDialog

class GUIUtils:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.root.geometry("800x600")
        self.create_login_gui()
        self.on_logout = None  

    def open_register_dialog(self):
        RegisterDialog(self.conn)

    def create_login_gui(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=20, pady=20)

        username_label = tk.Label(self.login_frame, text="Username:")
        username_label.grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        password_label = tk.Label(self.login_frame, text="Password:")
        password_label.grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        register_button = tk.Button(self.login_frame, text="Register", command=self.open_register_dialog)
        register_button.grid(row=3, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        # Perform authentication logic here...
        # Assuming authentication is successful, determine user type and proceed accordingly
        is_admin = self.check_admin(username)

        if is_admin:
            AdminGUI(self.root, username, self.conn, self)
            self.login_frame.destroy()
        else:
            UserGUI(self.root, username, self.conn, self)
            self.login_frame.destroy()

    def check_admin(self, username):
        # Perform admin check based on your database or any other criteria
        # Return True if the user is an admin, False otherwise
        cursor = self.conn.execute("SELECT COUNT(*) FROM admins WHERE username = ?", (username,))
        count = cursor.fetchone()[0]
        return count > 0

    def register_new_user(self, name, password, address, phone, reg_num, department, gender):
        try:
            # Insert new user into the database
            self.conn.execute("INSERT INTO users (username, password, address, phone, registration_number, department, gender) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (name, password, address, phone, reg_num, department, gender))
            self.conn.commit()
            messagebox.showinfo("Success", "User registered successfully. Please log in.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")

    def get_user_id(self, username):
        cursor = self.conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()
        if user_id:
            return user_id[0]
        else:
            return None
