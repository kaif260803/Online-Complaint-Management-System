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

        self.department_label = tk.Label(self.user_frame, text="Department:")
        self.department_label.grid(row=1, column=0, sticky="w")
        self.department_combobox = ttk.Combobox(self.user_frame, values=["Computer Science and Engineering", "Electrical Engineering", "Automobile Engineering", "Biotechnology"])
        self.department_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.department_combobox.current(0)

        self.submit_button = tk.Button(self.user_frame, text="Submit", command=self.add_complaint)
        self.submit_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.logout_button = tk.Button(self.user_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=3, column=0, columnspan=2, pady=10)

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

    def logout(self):
        self.user_frame.destroy()
        self.gui_utils.create_login_gui()
