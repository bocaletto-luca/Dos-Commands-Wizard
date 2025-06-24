# Software Name: Dos Commands Wizard
# Language: Italian
# Author: Bocaletto Luca
# Web Site: https://www.elektronoide.it
# Importa le librerie necessarie
import tkinter as tk  # Per la creazione dell'interfaccia grafica
import sqlite3  # Per la gestione del database
import subprocess  # Per l'esecuzione dei comandi shell
import threading  # Per la gestione dei thread
import time  # Per il controllo del tempo
import os
# Crea una connessione al database (o lo crea se non esiste)
conn = sqlite3.connect('custom_commands.db')
cursor = conn.cursor()

# Crea la tabella se non esiste
cursor.execute('''CREATE TABLE IF NOT EXISTS commands
                  (id INTEGER PRIMARY KEY,
                   name TEXT,
                   description TEXT)''')

# Definizione della classe principale dell'applicazione
class CommandWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dos Commands Wizard")
        self.geometry("600x400")

        # Crea l'interfaccia utente
        self.create_ui()
        self.is_scheduled = False
        self.scheduled_job = None

    def create_ui(self):
        # Creazione degli elementi dell'interfaccia utente
        self.command_entry = tk.Entry(self)
        self.command_entry.pack(fill=tk.X, padx=10, pady=10)

        self.interval_entry = tk.Entry(self)
        self.interval_entry.pack(fill=tk.X, padx=10, pady=5)
        self.interval_entry.insert(0, "5")

        self.schedule_button = tk.Button(self, text="Temporizza Comando", command=self.schedule_command)
        self.schedule_button.pack(pady=5)

        self.run_now_button = tk.Button(self, text="Esegui Subito", command=self.run_command_now)
        self.run_now_button.pack(pady=5)

        self.reset_button = tk.Button(self, text="Reset Temporizzazione", command=self.reset_schedule)
        self.reset_button.pack(pady=5)

        self.custom_commands_button = tk.Button(self, text="Lista Comandi", command=self.open_custom_commands_window)
        self.custom_commands_button.pack(pady=5)

        self.output_text = tk.Text(self, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.output_text.config(state=tk.DISABLED)

    # Metodo per eseguire un comando
    def run_command(self, command):
        try:
            if command.startswith("cd.."):
                # Esegui il cambio directory
                parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
                os.chdir(parent_dir)
                self.show_info(f"Directory corrente: {os.getcwd()}")
            else:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                self.display_output(output, 'stdout')
        except subprocess.CalledProcessError as e:
            error_output = e.output
            self.display_output(error_output, 'stderr')

    # Metodo per visualizzare l'output dell'esecuzione
    def display_output(self, output, tag):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, output, tag)
        self.output_text.tag_add(tag, '1.0', 'end')
        self.output_text.tag_config(tag, foreground='green' if tag == 'stdout' else 'red')
        self.output_text.config(state=tk.DISABLED)

    # Metodo per attivare/disattivare la temporizzazione
    def toggle_scheduling(self):
        self.is_scheduled = not self.is_scheduled

    # Metodo per eseguire un comando in modo programmato
    def schedule_execution(self, command, interval_seconds):
        time.sleep(interval_seconds)
        if self.is_scheduled:
            self.run_command(command)

    # Metodo per visualizzare messaggi informativi
    def show_info(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state=tk.DISABLED)

    # Metodo per programmare l'esecuzione di un comando
    def schedule_command(self):
        command = self.command_entry.get()
        interval_str = self.interval_entry.get()

        if not command:
            self.show_info("Inserisci un comando valido.")
            return

        try:
            interval_seconds = int(interval_str)
        except ValueError:
            self.show_info("Inserisci un intervallo di tempo valido (in secondi).")
            return

        if interval_seconds <= 0:
            self.show_info("L'intervallo di tempo deve essere superiore a 0.")
            return

        self.is_scheduled = True
        self.show_info(f"Temporizzazione attivata: esecuzione del comando '{command}' tra {interval_seconds} secondo/i...")
        if self.scheduled_job:
            self.scheduled_job.cancel()
        self.scheduled_job = threading.Timer(interval_seconds, self.run_command, args=(command,))
        self.scheduled_job.start()

    # Metodo per eseguire un comando immediatamente
    def run_command_now(self):
        command = self.command_entry.get()
        if not command:
            self.show_info("Inserisci un comando valido.")
            return
        self.run_command(command)

    # Metodo per annullare la temporizzazione
    def reset_schedule(self):
        self.is_scheduled = False
        if self.scheduled_job:
            self.scheduled_job.cancel()
        self.show_info("Temporizzazione annullata")

    # Metodo per aprire la finestra dei comandi personalizzati
    def open_custom_commands_window(self):
        custom_commands_window = CustomCommandsWindow(self)
        custom_commands_window.title("Lista Comandi Personalizzati")
        custom_commands_window.geometry("600x400")
        custom_commands_window.protocol("WM_DELETE_WINDOW", self.reload_custom_commands)
        custom_commands_window.mainloop()

    # Metodo per aggiornare i comandi personalizzati
    def reload_custom_commands(self):
        # Questo metodo viene chiamato quando la finestra "Lista Comandi" viene chiusa
        # Puoi implementare l'aggiornamento dei comandi personalizzati qui
        pass

# Definizione della classe per la finestra dei comandi personalizzati
class CustomCommandsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()  # Chiamare il costruttore della superclasse
        self.parent = parent
        self.create_ui()
        self.load_custom_commands()

    def create_ui(self):
        # Creazione dell'interfaccia per i comandi personalizzati
        self.custom_commands_listbox = tk.Listbox(self)
        self.custom_commands_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.name_entry = tk.Entry(self)
        self.name_entry.pack(fill=tk.X, padx=10, pady=5)
        self.name_entry.insert(0, "Nome Comando")

        self.description_entry = tk.Entry(self)
        self.description_entry.pack(fill=tk.X, padx=10, pady=5)
        self.description_entry.insert(0, "Descrizione")

        self.add_button = tk.Button(self, text="Aggiungi Comando", command=self.add_custom_command)
        self.add_button.pack(pady=5)

        self.edit_button = tk.Button(self, text="Modifica Comando", command=self.edit_custom_command)
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(self, text="Elimina Comando", command=self.delete_custom_command)
        self.delete_button.pack(pady=5)

        self.custom_commands_listbox.bind("<<ListboxSelect>>", self.select_custom_command)

    # Metodo per caricare i comandi personalizzati dal database
    def load_custom_commands(self):
        cursor.execute("SELECT id, name, description FROM commands")
        commands = cursor.fetchall()
        for command in commands:
            self.custom_commands_listbox.insert(tk.END, f"{command[1]} - {command[2]}")

    # Metodo per selezionare un comando personalizzato
    def select_custom_command(self, event):
        selected_index = self.custom_commands_listbox.curselection()
        if selected_index:
            selected_id = selected_index[0] + 1
            cursor.execute("SELECT name FROM commands WHERE id=?", (selected_id,))
            result = cursor.fetchone()
            selected_command = result[0]
            self.parent.command_entry.delete(0, tk.END)
            self.parent.command_entry.insert(0, selected_command)  # Inserisci il comando nella casella di input nella finestra principale

    # Metodo per aggiungere un nuovo comando personalizzato
    def add_custom_command(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        if name and description:
            cursor.execute("INSERT INTO commands (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            self.custom_commands_listbox.insert(tk.END, f"{name} - {description}")

    # Metodo per modificare un comando personalizzato esistente
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

    # Metodo per eliminare un comando personalizzato
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
