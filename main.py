import psutil
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import threading


class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Manager")
        self.default_bg = "#1e1e2e"
        
        # Set up GUI components
        self.notebook = ttk.Notebook(root)
        self.performance_tab = ttk.Frame(self.notebook)
        
        self.root.configure(background="#1e1e2e")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#1e1e2e", foreground="white", fieldbackground="#1e1e2e", highlightthickness=0)
        self.style.map("Treeview", background=[("selected", "#CBA6F7")], foreground=[("selected", "black")])
        
        self.process_tree = ttk.Treeview(root, columns=("PID", "Name", "Username", "Status", "Memory (%)", "CPU (%)"))
        self.process_tree.heading("#0", text="PID")
        self.process_tree.heading("#1", text="Name")
        self.process_tree.heading("#2", text="Username")
        self.process_tree.heading("#3", text="Status")
        self.process_tree.heading("#4", text="Memory (%)")
        self.process_tree.heading("#5", text="CPU (%)")
        self.process_tree.column("#0", width=100, minwidth=100, stretch=tk.NO)
        self.process_tree.column("#1", width=200, minwidth=100, stretch=tk.NO)
        self.process_tree.column("#2", width=150, minwidth=100, stretch=tk.NO)
        self.process_tree.column("#3", width=100, minwidth=100, stretch=tk.NO)
        self.process_tree.column("#4", width=100, minwidth=100, stretch=tk.NO)
        self.process_tree.column("#5", width=100, minwidth=100, stretch=tk.NO)
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.style.configure("Treeview.Heading", background="#313344", foreground="white", bordercolor="#313344")
        self.style.map("Treeview.Heading", background=[("active", "#313344")], bordercolor=[("active", "#313344")])
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
        self.search_entry.bind("<Return>", lambda event: self.search_process())

        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=5)

        self.kill_button = tk.Button(button_frame, text="End Task", fg="white", bg="#1e1e2e", command=self.kill_process)
        self.kill_button.pack(side=tk.LEFT, padx=5)
        self.root.bind("<Control-k>", lambda event: self.kill_process())

        self.refresh_button = tk.Button(button_frame, text="Refresh", fg="white", bg="#1e1e2e", command=self.update_processes)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        self.root.bind("<Control-r>", lambda event: self.update_processes())

        self.last_process_info = {}
        self.expanded_items = set()  # Set to store expanded items
        self.update_processes()
        self.schedule_update()

        self.process_tree.bind("<Double-1>", self.show_child_processes)

    def update_processes(self):
        selected_item = self.process_tree.selection()
        selected_pid = None
        if selected_item:
            selected_pid = int(self.process_tree.item(selected_item, "text"))
        
        self.expanded_items.clear()  # Clear the set before updating
        
        # Store expanded items
        for item in self.process_tree.get_children(""):
            if self.process_tree.item(item, "open"):
                self.expanded_items.add(item)
        
        self.process_tree.delete(*self.process_tree.get_children())
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'memory_percent', 'cpu_percent']):
            pid = proc.info['pid']
            memory_percent = proc.info['memory_percent']
            cpu_percent = proc.info['cpu_percent']

            if psutil.pid_exists(pid):
                process_name = proc.info['name']
                username = proc.info['username']
                status = proc.info['status']

                if self.is_parent_process(pid):
                    values = (process_name, username, status, f"{memory_percent:.2f}", f"{cpu_percent:.2f}")
                    self.process_tree.insert("", tk.END, text=str(pid), values=values)

                self.last_process_info[pid] = (memory_percent, cpu_percent)
        
        if selected_pid:
            for item in self.process_tree.get_children():
                if self.process_tree.item(item, "text") == str(selected_pid):
                    self.process_tree.selection_set(item)
                    self.process_tree.focus(item)
                    self.process_tree.see(item)
                    break
        
        # Expand previously expanded items
        for item in self.expanded_items:
            self.process_tree.item(item, open=True)

    def show_child_processes(self, event):
        threading.Thread(target=self.list_child_processes).start()

    def list_child_processes(self):
        item = self.process_tree.focus()
        pid = int(self.process_tree.item(item, "text")) 

        self.process_tree.delete(*self.process_tree.get_children(item))

        if self.is_parent_process(pid):
            children = list(psutil.Process(pid).children(recursive=True)) 
            if children:
                for child in children:
                    child_pid = child.pid
                    memory_percent = child.memory_percent()
                    cpu_percent = child.cpu_percent()  

                    try:
                        username = child.username()
                    except psutil.AccessDenied:
                        username = "N/A" 

                    values = (child.name(), username, child.status(), f"{memory_percent:.2f}", f"{cpu_percent:.2f}")
                    self.process_tree.insert(item, tk.END, text=str(child_pid), values=values) 
                    
            else:
                tkinter.messagebox.showerror("Error", "No child processes found for this parent process.") 
        else:
            tkinter.messagebox.showerror("Error", "Selected process is not a parent process.") 

    def kill_process(self):
        selected_item = self.process_tree.selection()
        if selected_item:
            pid = int(self.process_tree.item(selected_item, "text"))
            try:
                process = psutil.Process(pid)
                if not self.is_system_process(pid):
                    process.terminate()
                    self.update_processes()
                else:
                    tkinter.messagebox.showerror("Error", "Cannot terminate system processes.")
            except psutil.NoSuchProcess:
                tkinter.messagebox.showerror("Error", "The selected process no longer exists.")
            except psutil.AccessDenied:
                tkinter.messagebox.showerror("Error", "Access denied. You may not have sufficient privileges.")

    def is_parent_process(self, pid):
        try:
            process = psutil.Process(pid)
            if process.children():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return False

    def is_system_process(self, pid):
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
        search_text = self.search_entry.get().strip().lower()
        if search_text:
            found = self.recursive_search_process("", search_text)
            if not found:
                tkinter.messagebox.showerror("Search Result", f"No process with name '{search_text}' found.")

    def recursive_search_process(self, parent_item, search_text):
        found = False
        for item in self.process_tree.get_children(parent_item):
            name = self.process_tree.item(item, "values")[0].lower()
            if search_text in name:
                self.process_tree.selection_set(item)
                self.process_tree.focus(item)
                self.process_tree.see(item)
                found = True
                # If the search text is found, continue searching in child processes
                found_child = self.recursive_search_process(item, search_text)
                if found_child:
                    found = True
                    break
        return found

    def schedule_update(self):
        self.update_processes()
        self.root.after(15000, self.schedule_update)  

def main():
    root = tk.Tk()
    root.geometry("800x600")
    TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
