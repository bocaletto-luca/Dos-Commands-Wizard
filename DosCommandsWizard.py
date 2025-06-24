# Software Name: Dos Commands Wizard
# Language: English
# Author: Bocaletto Luca
# Web Site: https://bocaletto-luca.github.io
# Web Site: https://bocalettoluca.altervista.org
# Import necessary libraries
import tkinter as tk  # For creating the graphical interface
import sqlite3  # For database management
import subprocess  # For running shell commands
import threading  # For thread management
import time  # For time control
import os

# Create a connection to the database (or create it if it doesn't exist)
conn = sqlite3.connect('custom_commands.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS commands
                  (id INTEGER PRIMARY KEY,
                   name TEXT,
                   description TEXT)''')

# Define the main application class
class CommandWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dos Commands Wizard")
        self.geometry("600x400")

        # Create the user interface
        self.create_ui()
        self.is_scheduled = False
        self.scheduled_job = None

    def create_ui(self):
        # Create the user interface elements
        self.command_entry = tk.Entry(self)
        self.command_entry.pack(fill=tk.X, padx=10, pady=10)

        self.interval_entry = tk.Entry(self)
        self.interval_entry.pack(fill=tk.X, padx=10, pady=5)
        self.interval_entry.insert(0, "5")

        self.schedule_button = tk.Button(self, text="Schedule Command", command=self.schedule_command)
        self.schedule_button.pack(pady=5)

        self.run_now_button = tk.Button(self, text="Run Now", command=self.run_command_now)
        self.run_now_button.pack(pady=5)

        self.reset_button = tk.Button(self, text="Reset Schedule", command=self.reset_schedule)
        self.reset_button.pack(pady=5)

        self.custom_commands_button = tk.Button(self, text="Custom Commands List", command=self.open_custom_commands_window)
        self.custom_commands_button.pack(pady=5)

        self.output_text = tk.Text(self, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.output_text.config(state=tk.DISABLED)

    # Method to run a command
    def run_command(self, command):
        try:
            if command.startswith("cd.."):
                # Execute the directory change
                parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
                os.chdir(parent_dir)
                self.show_info(f"Current directory: {os.getcwd()}")
            else:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                self.display_output(output, 'stdout')
        except subprocess.CalledProcessError as e:
            error_output = e.output
            self.display_output(error_output, 'stderr')

    # Method to display the execution output
    def display_output(self, output, tag):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, output, tag)
        self.output_text.tag_add(tag, '1.0', 'end')
        self.output_text.tag_config(tag, foreground='green' if tag == 'stdout' else 'red')
        self.output_text.config(state=tk.DISABLED)

    # Method to toggle scheduling
    def toggle_scheduling(self):
        self.is_scheduled = not self.is_scheduled

    # Method to run a command in a scheduled manner
    def schedule_execution(self, command, interval_seconds):
        time.sleep(interval_seconds)
        if self.is_scheduled:
            self.run_command(command)

    # Method to display informative messages
    def show_info(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state=tk.DISABLED)

    # Method to schedule command execution
    def schedule_command(self):
        command = self.command_entry.get()
        interval_str = self.interval_entry.get()

        if not command:
            self.show_info("Enter a valid command.")
            return

        try:
            interval_seconds = int(interval_str)
        except ValueError:
            self.show_info("Enter a valid time interval (in seconds).")
            return

        if interval_seconds <= 0:
            self.show_info("Time interval must be greater than 0.")
            return

        self.is_scheduled = True
        self.show_info(f"Scheduling activated: executing command '{command}' in {interval_seconds} second(s)...")
        if self.scheduled_job:
            self.scheduled_job.cancel()
        self.scheduled_job = threading.Timer(interval_seconds, self.run_command, args=(command,))
        self.scheduled_job.start()

    # Method to run a command immediately
    def run_command_now(self):
        command = self.command_entry.get()
        if not command:
            self.show_info("Enter a valid command.")
            return
        self.run_command(command)

    # Method to cancel scheduling
    def reset_schedule(self):
        self.is_scheduled = False
        if self.scheduled_job:
            self.scheduled_job.cancel()
        self.show_info("Scheduling canceled")

    # Method to open the custom commands window
    def open_custom_commands_window(self):
        custom_commands_window = CustomCommandsWindow(self)
        custom_commands_window.title("Custom Commands List")
        custom_commands_window.geometry("600x400")
        custom_commands_window.protocol("WM_DELETE_WINDOW", self.reload_custom_commands)
        custom_commands_window.mainloop()

    # Method to update custom commands
    def reload_custom_commands(self):
        # This method is called when the "Custom Commands List" window is closed
        # You can implement the update of custom commands here
        pass

# Define the class for the custom commands window
class CustomCommandsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()  # Call the superclass constructor
        self.parent = parent
        self.create_ui()
        self.load_custom_commands()

    def create_ui(self):
        # Create the user interface for custom commands
        self.custom_commands_listbox = tk.Listbox(self)
        self.custom_commands_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.name_entry = tk.Entry(self)
        self.name_entry.pack(fill=tk.X, padx=10, pady=5)
        self.name_entry.insert(0, "Command Name")

        self.description_entry = tk.Entry(self)
        self.description_entry.pack(fill=tk.X, padx=10, pady=5)
        self.description_entry.insert(0, "Description")

        self.add_button = tk.Button(self, text="Add Command", command=self.add_custom_command)
        self.add_button.pack(pady=5)

        self.edit_button = tk.Button(self, text="Edit Command", command=self.edit_custom_command)
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(self, text="Delete Command", command=self.delete_custom_command)
        self.delete_button.pack(pady=5)

        self.custom_commands_listbox.bind("<<ListboxSelect>>", self.select_custom_command)

    # Method to load custom commands from the database
    def load_custom_commands(self):
        cursor.execute("SELECT id, name, description FROM commands")
        commands = cursor.fetchall()
        for command in commands:
            self.custom_commands_listbox.insert(tk.END, f"{command[1]} - {command[2]}")

    # Method to select a custom command
    def select_custom_command(self, event):
        selected_index = self.custom_commands_listbox.curselection()
        if selected_index:
            selected_id = selected_index[0] + 1
            cursor.execute("SELECT name FROM commands WHERE id=?", (selected_id,))
            result = cursor.fetchone()
            selected_command = result[0]
            self.parent.command_entry.delete(0, tk.END)
            self.parent.command_entry.insert(0, selected_command)  # Insert the command in the input box in the main window

    # Method to add a new custom command
    def add_custom_command(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        if name and description:
            cursor.execute("INSERT INTO commands (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            self.custom_commands_listbox.insert(tk.END, f"{name} - {description}")

    # Method to edit an existing custom command
    def edit_custom_command(self):
        selected_index = self.custom_commands_listbox.curselection()
        if selected_index:
            selected_id = selected_index[0] + 1
            name = self.name_entry.get()
            description = self.description_entry.get()
            if name and description:
                cursor.execute("UPDATE commands SET name=?, description=? WHERE id=?", (name, description, selected_id))
                conn.commit()
                self.custom_commands_listbox.delete(selected_index)
                self.custom_commands_listbox.insert(tk.END, f"{name} - {description}")

    # Method to delete a custom command
    def delete_custom_command(self):
        selected_index = self.custom_commands_listbox.curselection()
        if selected_index:
            selected_id = selected_index[0] + 1
            cursor.execute("DELETE FROM commands WHERE id=?", (selected_id,))
            conn.commit()
            self.custom_commands_listbox.delete(selected_index)

if __name__ == "__main__":
    app = CommandWindow()
    app.mainloop()
