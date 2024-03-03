import tkinter as tk
import sqlite3
from gui_utils import GUIUtils
from create_tables import create_tables

def main():
    create_tables()
    root = tk.Tk()
    conn = sqlite3.connect("online_management_system.db")
    gui_utils = GUIUtils(root, conn)
    root.mainloop()

if __name__ == "__main__":
    main()

