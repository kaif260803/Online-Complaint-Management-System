import tkinter as tk
from tkinter import messagebox

class AdminGUI:
    def __init__(self, root, username, conn, gui_utils):
        self.root = root
        self.username = username
        self.conn = conn
        self.gui_utils = gui_utils  # Store the GUIUtils instance
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

        self.user_info_label = tk.Label(self.admin_frame, text="User Information:")
        self.user_info_label.grid(row=0, column=2, sticky="w")
        self.user_info_text = tk.Text(self.admin_frame, width=60, height=10)
        self.user_info_text.grid(row=1, column=2, padx=10, pady=5)

        self.mark_done_button = tk.Button(self.admin_frame, text="Mark as Done", command=self.mark_complaint_done)
        self.mark_done_button.grid(row=4, column=2, padx=10, pady=5)

        self.load_normal_users()

        self.logout_button = tk.Button(self.admin_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=5, column=0, columnspan=3, pady=10)

    def load_user_info(self, event):
        selected_user = self.user_listbox.get(self.user_listbox.curselection())
        self.complaint_listbox_admin.delete(0, tk.END)
        self.user_info_text.delete(1.0, tk.END)  

        # Load user information for the selected user
        cursor = self.conn.execute("SELECT id, username, address, phone, registration_number, department FROM users WHERE username = ?", (selected_user,))
        user_info = cursor.fetchone()

        if user_info:
            user_id, username, address, phone, registration_number, department = user_info
            self.user_info_text.config(state=tk.NORMAL)  # Allow modifications temporarily
            self.user_info_text.delete(1.0, tk.END)
            self.user_info_text.insert(tk.END, f"Name: {username}\n")
            self.user_info_text.insert(tk.END, f"Address: {address}\n")
            self.user_info_text.insert(tk.END, f"Phone Number: {phone}\n")
            self.user_info_text.insert(tk.END, f"Registration Number: {registration_number}\n")
            self.user_info_text.insert(tk.END, f"Department: {department}\n")
            self.user_info_text.config(state=tk.DISABLED)  # Make it read-only again

            # Load complaints for the selected user
            cursor = self.conn.execute("SELECT id, complaint FROM complaints WHERE user_id = ?", (user_id,))
            for row in cursor:
                complaint_id, complaint = row
                self.complaint_listbox_admin.insert(tk.END, f"{complaint_id}: {complaint}")

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

    def logout(self):
        self.admin_frame.destroy()
        self.gui_utils.create_login_gui()

