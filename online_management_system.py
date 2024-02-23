import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
                            department TEXT NOT NULL,
                            is_admin INTEGER NOT NULL)''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS complaints (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            complaint TEXT NOT NULL,
                            department TEXT NOT NULL,
                            assigned_admin TEXT,
                            assigned_department TEXT,
                            status INTEGER DEFAULT 0,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id))''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS admins (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            department TEXT NOT NULL)''')

        self.conn.commit()

        # Insert admin data if it doesn't exist
        admins = [("Kaif", "yes", "Computer Science and Engineering"),
                  ("Sai", "yes", "Electrical Engineering"),
                  ("Rohit", "yes", "Automobile Engineering"),
                  ("Abhi", "yes", "Biotechnology")]
        for admin in admins:
            self.conn.execute("INSERT OR IGNORE INTO admins (username, password, department) VALUES (?, ?, ?)", admin)
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

        self.login_button = tk.Button(self.login_frame, text="Register", command=self.open_register_dialog)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=5)

    def open_register_dialog(self):
        RegisterDialog(self.root, self)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check users table for regular users
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
                return  # Exit the function after successful login

        # Check admins table for admin users
        cursor = self.conn.execute("SELECT password FROM admins WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row:
            stored_password = row[0]
            if password == stored_password:
                self.username = username
                self.create_admin_gui()
                return  # Exit the function after successful login

        # If username is not found in either table or password doesn't match
        messagebox.showwarning("Warning", "User not found or incorrect password. Please try again.")

    def register_new_user(self, name, password, department):
        self.conn.execute("INSERT INTO users (username, password, is_admin, department) VALUES (?, ?, 0, ?)", (name, password, department))
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

        self.user_label = tk.Label(self.admin_frame, text="User List:")
        self.user_label.grid(row=0, column=0, sticky="w")
        self.user_listbox = tk.Listbox(self.admin_frame, height=10)
        self.user_listbox.grid(row=1, column=0, padx=10, pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self.load_user_info)

        self.complaint_label_admin = tk.Label(self.admin_frame, text="Complaints:")
        self.complaint_label_admin.grid(row=0, column=1, sticky="w")
        self.complaint_listbox_admin = tk.Listbox(self.admin_frame, width=50)
        self.complaint_listbox_admin.grid(row=1, column=1, padx=10, pady=5)

        self.user_info_label = tk.Label(self.admin_frame, text="User Information:")
        self.user_info_label.grid(row=0, column=2, sticky="w")
        self.user_info_text = tk.Text(self.admin_frame, width=60, height=10)
        self.user_info_text.grid(row=1, column=2, padx=10, pady=5)

        self.department_label_admin = tk.Label(self.admin_frame, text="Department:")
        self.department_label_admin.grid(row=2, column=0, sticky="w")
        self.department_combobox_admin = ttk.Combobox(self.admin_frame)
        self.department_combobox_admin.grid(row=2, column=1, padx=10, pady=5)
        self.department_combobox_admin.bind("<<ComboboxSelected>>", self.load_admins)

        self.admin_label_admin = tk.Label(self.admin_frame, text="Admin List:")
        self.admin_label_admin.grid(row=3, column=0, sticky="w")
        self.admin_listbox_admin = tk.Listbox(self.admin_frame, height=5)
        self.admin_listbox_admin.grid(row=4, column=0, padx=10, pady=5)

        self.assign_button = tk.Button(self.admin_frame, text="Assign to", command=self.assign_complaint)
        self.assign_button.grid(row=4, column=1, padx=10, pady=5)

        self.mark_done_button = tk.Button(self.admin_frame, text="Mark as Done", command=self.mark_complaint_done)
        self.mark_done_button.grid(row=4, column=2, padx=10, pady=5)

        self.load_departments()  # Load departments for admin assignment
        self.load_normal_users()

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=5, column=0, columnspan=3, pady=10)

    def load_user_info(self, event):
        selected_user = self.user_listbox.get(self.user_listbox.curselection())
        self.complaint_listbox_admin.delete(0, tk.END)
        self.user_info_text.delete(1.0, tk.END)  

        # Load complaints for the selected user
        cursor = self.conn.execute("SELECT complaint, assigned_admin, assigned_department, timestamp FROM complaints WHERE user_id = (SELECT id FROM users WHERE username = ?)", (selected_user,))
        for row in cursor:
            complaint, assigned_admin, assigned_department, timestamp = row
            self.complaint_listbox_admin.insert(tk.END, f"Assigned to: {assigned_admin}, Department: {assigned_department}, {timestamp}: {complaint}")

        # Load user information for the selected user
        user_info = self.conn.execute("SELECT department FROM users WHERE username = ?", (selected_user,)).fetchone()
        if user_info:
            department = user_info[0]
            self.user_info_text.insert(tk.END, f"Department: {department}\n")

    def load_admins(self, event):
        selected_department = self.department_combobox_admin.get()
        self.admin_listbox_admin.delete(0, tk.END)

        cursor = self.conn.execute("SELECT username FROM admins WHERE department = ?", (selected_department,))
        for row in cursor:
            username = row[0]
            self.admin_listbox_admin.insert(tk.END, username)

    def assign_complaint(self):
        selected_complaint = self.complaint_listbox_admin.get(tk.ACTIVE)
        selected_admin = self.admin_listbox_admin.get(tk.ACTIVE)
        complaint_id = selected_complaint.split(":")[0]

        if selected_admin == "":
            messagebox.showerror("Error", "Please select an admin to assign the complaint.")
            return

        assigned_department = self.department_combobox_admin.get()

        self.conn.execute("UPDATE complaints SET user_id = (SELECT id FROM admins WHERE username = ?), assigned_admin = ?, assigned_department = ? WHERE id = ?", (selected_admin, selected_admin, assigned_department, complaint_id))
        self.conn.commit()
        messagebox.showinfo("Success", "Complaint assigned successfully.")

    def mark_complaint_done(self):
        selected_complaint = self.complaint_listbox_admin.get(tk.ACTIVE)
        complaint_id = selected_complaint.split(":")[0]

        self.conn.execute("UPDATE complaints SET status = 1 WHERE id = ?", (complaint_id,))
        self.conn.commit()
        messagebox.showinfo("Success", "Complaint marked as done.")

    def load_normal_users(self):
        cursor = self.conn.execute("SELECT username FROM users WHERE is_admin = 0")
        for row in cursor:
            username = row[0]
            self.user_listbox.insert(tk.END, username)

    def add_complaint(self):
        complaint = self.complaint_entry.get()
        department = self.department_combobox.get()

        if complaint:
            user_id = self.get_user_id(self.username)
            self.conn.execute("INSERT INTO complaints (user_id, complaint, department) VALUES (?, ?, ?)", (user_id, complaint, department))
            self.conn.commit()
            messagebox.showinfo("Success", "Complaint submitted successfully.")
            self.complaint_entry.delete(0, tk.END)
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

    def load_departments(self):
        departments = ["Computer Science and Engineering", "Electrical Engineering", "Automobile Engineering", "Biotechnology"]
        self.department_combobox_admin['values'] = departments

if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineManagementSystem(root)
    root.mainloop()

