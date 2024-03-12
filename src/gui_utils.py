import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .user_gui import UserGUI
from .admin_gui import AdminGUI
from .register_dialog import RegisterDialog

class GUIUtils:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.root.geometry("800x600")
        self.create_login_gui()
        self.on_logout = None  

    def quit_application(self):
        self.conn.close() # Closes the database connection
        self.root.quit()

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

        quit_button = tk.Button(self.login_frame, text="Quit", command=self.quit_application)
        quit_button.grid(row=4, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        cursor = self.conn.execute("SELECT password, is_admin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        cursor = self.conn.execute("SELECT password, is_admin FROM admins WHERE username = ?", (username,))
        row2 = cursor.fetchone()

        if row:
            stored_password, is_admin = row 
            if password == stored_password:
                self.username = username
                UserGUI(self.root, username, self.conn, self)
                self.login_frame.destroy()
            else:
                messagebox.showwarning("Warning", "Incorrect password. Please try again.")
        elif row2:
            stored_password, is_admin = row2
            if password == stored_password:
                self.username = username
                AdminGUI(self.root, username, self.conn, self)
                self.login_frame.destroy()
            else:
                messagebox.showwarning("Warning", "Incorrect password. Please try again.")
        else:
            messagebox.showwarning("Warning", "User not found. Please register.")

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
