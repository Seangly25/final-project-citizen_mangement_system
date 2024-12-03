import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect('village_management.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citizens (
            id TEXT PRIMARY KEY,
            name TEXT,
            sex TEXT,
            age INTEGER,
            dob TEXT,
            occupation TEXT,
            address TEXT,
            father_name TEXT,
            father_dob TEXT,
            mother_name TEXT,
            mother_dob TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Main application class
class VillageManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Village Population Management")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.current_manager = None
        
        self.create_widgets()
        setup_database()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Village Population Management", font=("Helvetica", 24), bg="#4CAF50", fg="white")
        title.pack(pady=20)

        # Login Frame
        self.login_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:", bg="#f0f0f0").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:", bg="#f0f0f0").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=10)
        tk.Button(self.login_frame, text="Sign Up", command=self.sign_up).grid(row=3, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        conn = sqlite3.connect('village_management.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM managers WHERE username=? AND password=?", (username, password))
        manager = cursor.fetchone()
        
        if manager:
            self.current_manager = manager[1]
            messagebox.showinfo("Success", f"Welcome {self.current_manager}")
            self.show_citizen_management()
        else:
            messagebox.showerror("Error", "Invalid username or password")
        
        conn.close()

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute("INSERT INTO managers (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Sign up successful! You can now log in.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            
            conn.close()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def show_citizen_management(self):
        for widget in self.login_frame.winfo_children():
            widget.destroy()

        # Citizen Management Frame
        citizen_frame = tk.Frame(self.root, bg="#f0f0f0")
        citizen_frame.pack(pady=20)

        tk.Button(citizen_frame, text="Add Citizen", command=self.add_citizen).pack(pady=5)
        tk.Button(citizen_frame, text="View Citizens", command=self.view_citizens).pack(pady=5)
        tk.Button(citizen_frame, text="Search Citizen", command=self.search_citizen).pack(pady=5)
        tk.Button(citizen_frame, text="Change Citizen Info", command=self.change_citizen).pack(pady=5)
        tk.Button(citizen_frame, text="Delete Citizen", command=self.delete_citizen).pack(pady=5)

    def add_citizen(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Citizen")

        labels = ["ID (6-digit):", "Name:", "Sex:", "Age:", "Date of Birth:", 
                  "Occupation:", "Address:", "Father's Name:", 
                  "Father's DOB:", "Mother's Name:", "Mother's DOB:"]
        
        entries = []
        
        for label in labels:
            tk.Label(add_window, text=label).pack()
            entry = tk.Entry(add_window)
            entry.pack()
            entries.append(entry)
        
        def save_citizen():
            citizen_data = [entry.get() for entry in entries]
            
            if len(citizen_data[0]) != 6 or not citizen_data[0].isdigit():
                messagebox.showerror("Error", "ID must be a 6-digit number.")
                return
            
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO citizens (id, name, sex, age, dob, occupation, address, father_name, father_dob, mother_name, mother_dob) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', citizen_data)
                conn.commit()
                messagebox.showinfo("Success", "Citizen added successfully!")
                add_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Citizen ID must be unique.")
            
            conn.close()

        tk.Button(add_window, text="Save Citizen", command=save_citizen).pack(pady=10)

    def view_citizens(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("View Citizens")

        tree = ttk.Treeview(view_window, columns=("ID", "Name", "Sex", "Age", "DOB", 
                                                   "Occupation", "Address", "Father's Name", 
                                                   "Father's DOB", "Mother's Name", 
                                                   "Mother's DOB"), show='headings')

        for col in tree["columns"]:
            tree.heading(col, text=col)
        
        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(view_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        conn = sqlite3.connect('village_management.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM citizens ORDER BY id ASC")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        conn.close()

    def search_citizen(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Citizen")

        tk.Label(search_window, text="Enter Citizen ID:").pack(pady=10)
        
        id_entry = tk.Entry(search_window)
        id_entry.pack(pady=10)

        def find_citizen():
            citizen_id = id_entry.get()
            
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM citizens WHERE id=?", (citizen_id,))
            citizen = cursor.fetchone()

            if citizen:
                result_str = f"ID: {citizen[0]}, Name: {citizen[1]}, Sex: {citizen[2]}, Age: {citizen[3]}, DOB: {citizen[4]}, Occupation: {citizen[5]}, Address: {citizen[6]}, Father's Name: {citizen[7]}, Father's DOB: {citizen[8]}, Mother's Name: {citizen[9]}, Mother's DOB: {citizen[10]}"
                messagebox.showinfo("Citizen Found", result_str)
            else:
                messagebox.showerror("Error", f"No citizen found with ID {citizen_id}.")
            
            conn.close()

        tk.Button(search_window, text="Search Citizen", command=find_citizen).pack(pady=10)

    def change_citizen(self):
        change_window = tk.Toplevel(self.root)
        change_window.title("Change Citizen Info")

        tk.Label(change_window, text="Enter Citizen ID to update:").pack(pady=10)
        
        id_entry = tk.Entry(change_window)
        id_entry.pack(pady=10)

        def load_citizen():
            citizen_id = id_entry.get()
            
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM citizens WHERE id=?", (citizen_id,))
            citizen = cursor.fetchone()

            if citizen:
                for i in range(1, len(citizen)):
                    entry_fields[i-1].delete(0, tk.END)
                    entry_fields[i-1].insert(0, citizen[i])
                
                update_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", f"No citizen found with ID {citizen_id}.")
            
            conn.close()

        entry_labels = ["Name:", "Sex:", "Age:", "Date of Birth:", 
                        "Occupation:", "Address:", "Father's Name:", 
                        "Father's DOB:", "Mother's Name:", 
                        "Mother's DOB:"]
        
        entry_fields = []
        
        for label in entry_labels:
            tk.Label(change_window, text=label).pack()
            entry_field = tk.Entry(change_window)
            entry_field.pack()
            entry_fields.append(entry_field)

        load_button = tk.Button(change_window, text="Load Citizen Info", command=load_citizen)
        load_button.pack(pady=10)

        update_button = tk.Button(change_window, text="Update Citizen Info", state=tk.DISABLED)

        def save_update():
            updated_data = [entry.get() for entry in entry_fields]
            
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE citizens SET name=?, sex=?, age=?, dob=?, occupation=?, address=?, father_name=?, father_dob=?, mother_name=?, mother_dob=? WHERE id=?
            ''', (*updated_data, id_entry.get()))
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"Citizen with ID {id_entry.get()} updated successfully!")
                change_window.destroy()
                
            conn.commit()
            conn.close()

        update_button.config(command=save_update)
        
        update_button.pack(pady=10)

    def delete_citizen(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Citizen")

        tk.Label(delete_window, text="Enter Citizen ID to delete:").pack(pady=10)
        
        id_entry = tk.Entry(delete_window)
        id_entry.pack(pady=10)

        def confirm_delete():
            citizen_id = id_entry.get()
            
            conn = sqlite3.connect('village_management.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM citizens WHERE id=?", (citizen_id,))
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", f"Citizen with ID {citizen_id} deleted successfully!")
                delete_window.destroy()
            else:
                messagebox.showerror("Error", f"No citizen found with ID {citizen_id}.")
            
            conn.commit()
            conn.close()

        tk.Button(delete_window, text="Delete Citizen", command=confirm_delete).pack(pady=10)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VillageManagementApp(root)
    root.mainloop()
