import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

        self.gender_label = tk.Label(self.dialog, text="Gender:")
        self.gender_label.grid(row=2, column=0, sticky="w")
        self.gender_combobox = ttk.Combobox(self.dialog, values=["Male", "Female", "Other"])
        self.gender_combobox.grid(row=2, column=1, padx=10, pady=5)

        self.address_label = tk.Label(self.dialog, text="Address:")
        self.address_label.grid(row=3, column=0, sticky="w")
        self.address_entry = tk.Entry(self.dialog)
        self.address_entry.grid(row=3, column=1, padx=10, pady=5)

        self.phone_label = tk.Label(self.dialog, text="Mobile Number:")
        self.phone_label.grid(row=4, column=0, sticky="w")
        self.phone_entry = tk.Entry(self.dialog)
        self.phone_entry.grid(row=4, column=1, padx=10, pady=5)

        self.reg_num_label = tk.Label(self.dialog, text="Registration Number:")
        self.reg_num_label.grid(row=5, column=0, sticky="w")
        self.reg_num_entry = tk.Entry(self.dialog)
        self.reg_num_entry.grid(row=5, column=1, padx=10, pady=5)

        self.register_button = tk.Button(self.dialog, text="Register", command=self.register_user)
        self.register_button.grid(row=6, column=0, columnspan=2, pady=10)

    def register_user(self):
        name = self.name_entry.get().strip()  # Strip leading and trailing whitespaces
        password = self.password_entry.get()
        gender = self.gender_combobox.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        reg_num = self.reg_num_entry.get()

        if not name:
            messagebox.showerror("Error", "Please enter a username.")
            return

        cursor = self.system.conn.execute("SELECT username FROM users WHERE username = ?", (name,))
        existing_user = cursor.fetchone()
        if existing_user:
            messagebox.showerror("Error", "Username already exists. Please choose another username.")
            return

        if password and gender and address and phone and reg_num:
            self.system.register_new_user(name, password, gender, address, phone, reg_num)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

