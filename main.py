import psutil
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox


class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Manager")
        self.root.iconphoto(True, tk.PhotoImage(file="C:\\Users\\chess\\OneDrive\\Desktop\\Task-Manager\\icon.png"))
        self.default_bg = "#1e1e2e"
        
        # Set the background color of the root window
        self.root.configure(background="#1e1e2e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#1e1e2e", foreground="white", fieldbackground="#1e1e2e", highlightthickness=0)
        self.style.map("Treeview", background=[("selected", "#CBA6F7")],foreground=[("selected", "black")])

        self.process_tree = ttk.Treeview(root, columns=("PID", "Name", "Username", "Status", "Memory (%)", "CPU (%)") )
        self.process_tree.heading("#0", text="PID")
        self.process_tree.heading("#1", text="Name")
        self.process_tree.heading("#2", text="Username")
        self.process_tree.heading("#3", text="Status")
        self.process_tree.heading("#4", text="Memory (%)")
        self.process_tree.heading("#5", text="CPU (%)")
        self.process_tree.column("#0", width=100,minwidth=100, stretch=tk.NO)
        self.process_tree.column("#1", width=200,minwidth=100, stretch=tk.NO)
        self.process_tree.column("#2", width=150,minwidth=100, stretch=tk.NO)
        self.process_tree.column("#3", width=100,minwidth=100, stretch=tk.NO)
        self.process_tree.column("#4", width=100,minwidth=100, stretch=tk.NO)
        self.process_tree.column("#5", width=100,minwidth=100, stretch=tk.NO)
        self.style.configure("Treeview",font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.style.configure("Treeview.Heading", background="#313344", foreground="white",bordercolor="#313344")
        self.style.map("Treeview.Heading", background=[("active", "#313344")],bordercolor=[("active", "#313344")])
        self.process_tree.pack(expand=True, fill=tk.BOTH)

        search_frame = tk.Frame(root, bg="#1e1e2e")
        search_frame.pack(pady=5)

        self.search_label = tk.Label(search_frame, text="Search Process:", fg="white", bg="#1e1e2e")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(search_frame, fg="white", bg="#313244", insertbackground="white")
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(search_frame, text="Search", fg="white", bg="#1e1e2e", command=self.search_process)
        self.search_button.pack(side=tk.LEFT, padx=5)
        self.style.configure("TButton", font=("Arial", 10))
        self.search_entry.bind("<Return>", lambda event: self.search_process())  # Bind Enter key to search function


        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=5)

        self.kill_button = tk.Button(button_frame, text="End Task", fg="white", bg="#1e1e2e", command=self.kill_process)
        self.kill_button.pack(side=tk.LEFT, padx=5)
        self.root.bind("<Control-k>", lambda event: self.kill_process())  # Bind Ctrl + K to kill process function


        self.refresh_button = tk.Button(button_frame, text="Refresh", fg="white", bg="#1e1e2e", command=self.update_processes)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        self.root.bind("<Control-r>", lambda event: self.update_processes())

        self.last_process_info = {}  # Store last known memory and CPU percentages
        self.update_processes()  # Initial update
        self.schedule_update()  # Start real-time updating

    def update_processes(self):
        selected_item = self.process_tree.selection()
        selected_pid = None
        if selected_item:
            selected_pid = int(self.process_tree.item(selected_item, "text"))
        
        self.process_tree.delete(*self.process_tree.get_children())
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'memory_percent', 'cpu_percent']):
            pid = proc.info['pid']
            memory_percent = proc.info['memory_percent']
            cpu_percent = proc.info['cpu_percent']

            # Check if the process exists before accessing its properties
            if psutil.pid_exists(pid):
                process_name = proc.info['name']
                username = proc.info['username']
                status = proc.info['status']

                values = ( process_name, username, status, f"{memory_percent:.2f}", f"{cpu_percent:.2f}")
                self.process_tree.insert("", tk.END, text=str(pid), values=values)

                # Update last known memory and CPU percentages
                self.last_process_info[pid] = (memory_percent, cpu_percent)
        
        if selected_pid:
            for item in self.process_tree.get_children():
                if self.process_tree.item(item, "text") == str(selected_pid):
                    self.process_tree.selection_set(item)
                    self.process_tree.focus(item)
                    self.process_tree.see(item)
                    break

    def kill_process(self):
        selected_item = self.process_tree.selection()
        if selected_item:
            pid = int(self.process_tree.item(selected_item, "text"))
            if not self.is_system_process(pid):
                process = psutil.Process(pid)
                process.terminate()
                self.update_processes()
            else:
                tkinter.messagebox.showerror("Error", "Cannot terminate system processes.")

    def is_system_process(self, pid):
        # Check if the process name is in a list of system processes
        system_processes = ["System", "Idle"]
        process_name = self.get_process_name(pid)
        if process_name in system_processes:
            return True
        return False

    def get_process_name(self, pid):
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return process.name()
        return None

    def search_process(self):
        search_text = self.search_entry.get().strip()
        if search_text:
            found = False
            for item in self.process_tree.get_children():
                name = self.process_tree.item(item, "values")[0]  # Get process name
                if search_text.lower() in name.lower():  # Case insensitive search
                    self.process_tree.selection_set(item)
                    self.process_tree.focus(item)
                    self.process_tree.see(item)
                    found = True
                    break
            if not found:
                tkinter.messagebox.showerror("Search Result", f"No process with name '{search_text}' found.")

    def schedule_update(self):
        self.update_processes()
        self.root.after(15000, self.schedule_update)  
        
def main():
    root = tk.Tk()
    root.geometry("800x600")
    TaskManagerGUI(root)
    root.mainloop()
    style= ttk.Style()

if __name__ == "__main__":
    main()

