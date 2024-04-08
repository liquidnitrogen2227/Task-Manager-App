import psutil
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter import *

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Manager")
        self.root.iconphoto(True, tk.PhotoImage(file="C:\\Users\\chess\\OneDrive\\Desktop\\Task-Manager\\icon.png"))
        self.default_bg = "#1e1e2e"
        

        self.process_tree = ttk.Treeview(root, columns=("PID", "Name", "Username", "Status", "Memory (%)", "CPU (%)"))
        self.process_tree.heading("#0", text="PID")
        self.process_tree.heading("#1", text="Name")
        self.process_tree.heading("#2", text="Username")
        self.process_tree.heading("#3", text="Status")
        self.process_tree.heading("#4", text="Memory (%)")
        self.process_tree.heading("#5", text="CPU (%)")
        self.process_tree.column("#0", width=100)
        self.process_tree.column("#1", width=200)
        self.process_tree.column("#2", width=150)
        self.process_tree.column("#3", width=100)
        self.process_tree.column("#4", width=100)
        self.process_tree.column("#5", width=100)
        self.process_tree.pack(expand=True, fill=tk.BOTH)

        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)

        self.search_label = tk.Label(search_frame, text="Search PID:",fg="white", bg="#1e1e2e")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(search_frame,fg="white", bg="#1e1e2e")
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(search_frame, text="Search",fg="white", bg="#1e1e2e", command=self.search_process)
        self.search_button.pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.kill_button = tk.Button(button_frame, text="End Task", fg="white", bg="#1e1e2e",command=self.kill_process)
        self.kill_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = tk.Button(button_frame, text="Refresh", fg="white", bg="#1e1e2e",command=self.update_processes)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.last_process_info = {}  # Store last known memory and CPU percentages
        self.update_processes()  # Initial update
        self.schedule_update()  # Start real-time updating
        self.root.configure(background="#1e1e2e")
        

    def update_processes(self):
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
            for item in self.process_tree.get_children():
                pid = self.process_tree.item(item, "text")
                if search_text == pid:
                    self.process_tree.selection_set(item)
                    self.process_tree.focus(item)
                    self.process_tree.see(item)
                    break
            else:
                tkinter.messagebox.showerror("Search Result", f"No process with PID '{search_text}' found.")

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
