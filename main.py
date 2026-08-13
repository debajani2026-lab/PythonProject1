import tkinter as tk
from tkinter import messagebox
from admin_auth import check_logS
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System - Login")
        self.root.geometry("350x220")
        self.root.resizable(False, False)

        tk.Label(root, text="Hospital Management System",
                 font=("Arial", 13, "bold")).pack(pady=15)

        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:").pack()
        self.password_entry = tk.Entry(root, width=30, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", width=15, command=self.handle_login,
                  bg="#3B8BD4", fg="white").pack(pady=15)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing info", "Username and password diye hobe.")
            return

        admin = check_login(username, password)

        if admin:
            messagebox.showinfo("Success", f"Welcome, {admin['full_name']}!")
            self.root.destroy()
            open_dashboard()
        else:
            messagebox.showerror("Login failed", "Username ba password bhul.")


def open_dashboard():
    from dashboard import Dashboard
    dash_root = tk.Tk()
    Dashboard(dash_root)
    dash_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()