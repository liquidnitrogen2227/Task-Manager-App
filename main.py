import psutil
import tkinter as tk
from tkinter import ttk

class TaskManager:
    
    def __init__(self,root):
        self.root = root
        self.root.title("Task Manager")
        self.process_tree = ttk.Treeview(root, columns=("PID", "Name", "Username", "Status"))
        self.process_tree.heading("#0", text="PID")
        self.process_tree.heading("#1", text="Name")
        self.process_tree.heading("#2", text="Username")
        self.process_tree.heading("#3", text="Status")
        self.process_tree.column("#0", width=100)
        self.process_tree.column("#1", width=200)
        self.process_tree.column("#2", width=150)
        self.process_tree.column("#3", width=100)
        
    def kill_process(self):
        selected_item = self.process_tree.selection()
        
    def update_processes(self):
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            print("PID: ", proc.pid)
    
        
        
def main():
    root = tk.Tk()
    TaskManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()