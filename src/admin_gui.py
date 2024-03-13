import tkinter as tk
from tkinter import messagebox

class AdminGUI:
    def __init__(self, root, username, conn, gui_utils):
        self.root = root
        self.username = username
        self.conn = conn
        self.gui_utils = gui_utils  # Store the GUIUtils instance
        self.complaint_combobox = tk.StringVar()
        self.create_admin_gui()

    def create_admin_gui(self):
        self.admin_frame = tk.Frame(self.root)
        self.admin_frame.pack(padx=20, pady=20)
        self.root.geometry("800x600")

        self.user_label = tk.Label(self.admin_frame, text="User List:")
        self.user_label.grid(row=0, column=0, sticky="w")
        self.user_listbox = tk.Listbox(self.admin_frame, height=10)
        self.user_listbox.grid(row=1, column=0, padx=10, pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self.load_user_info)

        self.complaint_label_admin = tk.Label(self.admin_frame, text="Complaints:")
        self.complaint_label_admin.grid(row=0, column=1, sticky="w")
        self.complaint_listbox_admin = tk.Listbox(self.admin_frame, width=50)
        self.complaint_listbox_admin.grid(row=1, column=1, padx=10, pady=5)

        self.assign_label = tk.Label(self.admin_frame, text="Assign complaint:")
        self.assign_label.grid(row=2, column=0, sticky="w")

        # Fetch complaint list from the database query
        cursor = self.conn.execute("SELECT id, complaint FROM complaints WHERE status = 0")
        complaints = [f"{row[0]}: {row[1]}" for row in cursor.fetchall()]

        if not complaints:
            complaints = ["Select complaint"]

        self.complaint_combobox.set(complaints[0])  # Set initial value

        # Create OptionMenu with complaints list
        self.complaint_dropdown = tk.OptionMenu(self.admin_frame, self.complaint_combobox, *complaints)
        self.complaint_dropdown.grid(row=2, column=1, padx=10, pady=5)

        # Fetch admin list from the database query
        cursor = self.conn.execute("SELECT username FROM admins")
        admins = [row[0] for row in cursor.fetchall()]

        self.admin_label = tk.Label(self.admin_frame, text="Select Admin:")
        self.admin_label.grid(row=2, column=2, sticky="w")
        self.admin_combobox = tk.StringVar()
        self.admin_combobox.set("Select admin")
        self.admin_dropdown = tk.OptionMenu(self.admin_frame, self.admin_combobox, *admins)
        self.admin_dropdown.grid(row=2, column=3, padx=10, pady=5)

        self.user_info_label = tk.Label(self.admin_frame, text="User Information:")
        self.user_info_label.grid(row=0, column=2, sticky="w")
        self.user_info_text = tk.Text(self.admin_frame, width=60, height=10)
        self.user_info_text.grid(row=1, column=2, padx=10, pady=5)

        self.mark_done_button = tk.Button(self.admin_frame, text="Mark as Done", command=self.mark_complaint_done)
        self.mark_done_button.grid(row=4, column=2, padx=10, pady=5)

        self.assign_button = tk.Button(self.admin_frame, text="Assign", command=self.assign_complaint)
        self.assign_button.grid(row=2, column=4, padx=10, pady=5)

        self.load_normal_users()

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=5, column=0, columnspan=5, pady=10)

    def load_user_info(self, event):
        selected_user = self.user_listbox.get(self.user_listbox.curselection())
        if not selected_user:
            return

        cursor = self.conn.execute("SELECT id, username, address, phone, gender, registration_number, department FROM users WHERE username = ?", (selected_user,))
        user_info = cursor.fetchone()

        if user_info:
            user_id, username, address, phone, gender, registration_number, department = user_info
            self.user_info_text.config(state=tk.NORMAL)  # Allow modifications temporarily
            self.user_info_text.delete(1.0, tk.END)
            self.user_info_text.insert(tk.END, f"Name: {username}\n")
            self.user_info_text.insert(tk.END, f"Address: {address}\n")
            self.user_info_text.insert(tk.END, f"Phone Number: {phone}\n")
            self.user_info_text.insert(tk.END, f"Gender: {gender}\n")
            self.user_info_text.insert(tk.END, f"Registration Number: {registration_number}\n")
            self.user_info_text.insert(tk.END, f"Department: {department}\n")
            self.user_info_text.config(state=tk.DISABLED)  # Make it read-only again

            # Pass user_id to load_user_complaints
            self.load_user_complaints(user_id)

    def load_user_complaints(self, user_id):
        # Fetch complaint list for the selected user from the database query
        cursor = self.conn.execute("SELECT id, complaint, status, assigned_admin, timestamp FROM complaints WHERE user_id = ?", (user_id,))
        complaints = []
        for row in cursor.fetchall():
            complaint_id, complaint_text, status, assigned_admin, timestamp = row
            if status:  # If complaint is marked as done
                complaint_info = f"{complaint_id}: {complaint_text}: Done by {assigned_admin} ({timestamp})"
            else:  # If complaint is not done
                if assigned_admin:  # If complaint is assigned to an admin
                    complaint_info = f"{complaint_id}: {complaint_text}: Not done, assigned to {assigned_admin} ({timestamp})"
                else:  # If complaint is not assigned to anyone
                    complaint_info = f"{complaint_id}: {complaint_text}: Not done, not assigned ({timestamp})"
            complaints.append(complaint_info)

        self.complaint_listbox_admin.delete(0, tk.END)  # Clear previous complaints
        if complaints:
            for complaint in complaints:
                self.complaint_listbox_admin.insert(tk.END, complaint)
        else:
            self.complaint_listbox_admin.insert(tk.END, "No complaints")

        # Set the default value for OptionMenu
        self.complaint_combobox.set("No complaints")

    def mark_complaint_done(self):
        selected_complaint = self.complaint_listbox_admin.get(tk.ACTIVE)
        
        if not selected_complaint:
            messagebox.showwarning("No Complaint Selected", "Please select a complaint to mark as done.")
            return

        complaint_id = selected_complaint.split(":")[0]

        # Fetch the assigned admin for the selected complaint
        cursor = self.conn.execute("SELECT assigned_admin FROM complaints WHERE id = ?", (complaint_id,))
        assigned_admin = cursor.fetchone()[0]

        # Check if the logged-in user is an admin and is the assigned admin for the complaint
        if self.username not in assigned_admin:
            messagebox.showerror("Error", "You are not authorized to mark this complaint as done.")
            return

        self.conn.execute("UPDATE complaints SET status = 1 WHERE id = ?", (complaint_id,))
        self.conn.commit()
        messagebox.showinfo("Success", "Complaint marked as done.")

    def assign_complaint(self):
        selected_user = self.user_listbox.get(self.user_listbox.curselection())
        if not selected_user:
            messagebox.showerror("Error", "Please select a user.")
            return

        selected_complaint = self.complaint_combobox.get().split(":")[0]
        selected_admin = self.admin_combobox.get()

        if selected_complaint == "Select complaint" or selected_admin == "Select admin":
            messagebox.showerror("Error", "Please select both complaint and admin.")
            return

        self.conn.execute("UPDATE complaints SET assigned_admin = ?, assigned_department = (SELECT department FROM admins WHERE username = ?) WHERE id = ?", (selected_admin, selected_admin, selected_complaint))
        self.conn.commit()
        messagebox.showinfo("Success", "Complaint assigned successfully.")

    def load_normal_users(self):
        cursor = self.conn.execute("SELECT username FROM users WHERE is_admin = 0")
        for row in cursor:
            username = row[0]
            self.user_listbox.insert(tk.END, username)

    def logout(self):
        self.admin_frame.destroy()
        self.gui_utils.create_login_gui()

