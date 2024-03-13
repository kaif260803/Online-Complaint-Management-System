import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class UserGUI:
    def __init__(self, root, username, conn, gui_utils):
        self.root = root
        self.username = username
        self.conn = conn
        self.gui_utils = gui_utils
        self.create_user_gui()

    def create_user_gui(self):
        self.user_frame = tk.Frame(self.root)
        self.user_frame.pack(padx=20, pady=20)
        self.root.geometry("800x600")

        self.complaint_label = tk.Label(self.user_frame, text="Complaint:")
        self.complaint_label.grid(row=0, column=0, sticky="w")
        self.complaint_entry = tk.Entry(self.user_frame)
        self.complaint_entry.grid(row=0, column=1, padx=10, pady=5)

        # Fetch department names from the database query
        cursor = self.conn.execute("SELECT dept_name FROM departments")
        departments = [row[0] for row in cursor.fetchall()]

        self.department_label = tk.Label(self.user_frame, text="Department:")
        self.department_label.grid(row=1, column=0, sticky="w")
        self.department_combobox = ttk.Combobox(self.user_frame, values=departments)
        self.department_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.department_combobox.current(0)

        self.submit_button = tk.Button(self.user_frame, text="Submit", command=self.add_complaint)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.complaints_label = tk.Label(self.user_frame, text="Your Complaints:")
        self.complaints_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.complaints_text = tk.Text(self.user_frame, height=10, width=200)
        self.complaints_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.logout_button = tk.Button(self.user_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.update_complaints_text()

    def add_complaint(self):
        complaint = self.complaint_entry.get()
        department = self.department_combobox.get()

        if not complaint:
            messagebox.showerror("Error", "Please enter a complaint.")
            return
        try:
            user_id = self.gui_utils.get_user_id(self.username)
            self.conn.execute("INSERT INTO complaints (user_id, complaint, department) VALUES (?, ?, ?)", (user_id, complaint, department))
            self.conn.commit()
            messagebox.showinfo("Success", "Complaint submitted successfully.")
            self.complaint_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit complaint: {e}")

    def update_complaints_text(self):
        try:
            user_id = self.gui_utils.get_user_id(self.username)
            cursor = self.conn.execute("SELECT complaint, department, assigned_admin, status FROM complaints WHERE user_id=?", (user_id,))
            complaints = cursor.fetchall()
            if complaints:
                complaints_text = ""
                for complaint, department, assigned_admin, status in complaints:
                    assigned_to = "Assigned to: " + assigned_admin if assigned_admin else "Assigned to: None"
                    complaint_info = f"Complaint: {complaint}, Department: {department}, {assigned_to}"
                    status_info = "Status: " + 'Done' if status else 'Not Done'
                    complaints_text += f"{complaint_info}, {status_info}\n"
            else:
                complaints_text = "No complaints found."
            self.complaints_text.config(state='normal')
            self.complaints_text.delete(1.0, tk.END)
            self.complaints_text.insert(tk.END, complaints_text)
            self.complaints_text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch complaints: {e}")

    def logout(self):
        self.user_frame.destroy()
        self.gui_utils.create_login_gui()
