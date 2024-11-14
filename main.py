import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

def parse_iso_datetime(date_str):
    date_str = date_str.replace('Z', '')
    date_str = date_str.split('.')[0]
    return datetime.fromisoformat(date_str)

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Нотатки")
        self.root.geometry("600x700")

        self.access_token = None
        self.user_id = None
        self.notes = []
        self.selected_note = None

        self.create_widgets()

        if not os.path.exists("auth.txt"):
            self.authorize()
        else:
            with open("auth.txt", "r") as f:
                self.user_id = f.read().strip()
            self.fetch_access_token()

    def authorize(self):
        code_window = tk.Toplevel(self.root)
        code_window.title("Авторизація")

        tk.Label(code_window, text="Введіть код з Telegram або залиште порожнім для створення нового акаунту").pack(pady=10)
        code_entry = ttk.Entry(code_window, font=("Helvetica", 14))
        code_entry.pack(pady=5)

        def submit_code():
            code = code_entry.get()
            if code:
                if self.verify_code(code):
                    code_window.destroy()
                else:
                    messagebox.showerror("Помилка", "Невірний код!")
            else:
                if self.create_new_account():
                    code_window.destroy()
                else:
                    messagebox.showerror("Помилка", "Не вдалося створити новий акаунт.")

        submit_button = ttk.Button(code_window, text="Відправити", command=submit_code)
        submit_button.pack(pady=5)

    def verify_code(self, code):
        try:
            response = requests.post("https://api.walletellaw.store/verify-code", json={"code": code})
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get("id")
                print(data)

                with open("auth.txt", "w") as f:
                    f.write(str(self.user_id))

                self.fetch_access_token()
                return True
            else:
                messagebox.showerror("Помилка", "Невірний код!")
                return False
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит не виконано: {e}")
            return False

    def create_new_account(self):
        try:
            response = requests.post("https://api.walletellaw.store/create-account")
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("id")
                print(data)

                with open("auth.txt", "w") as f:
                    f.write(str(self.user_id))

                self.fetch_access_token()
                return True
            else:
                messagebox.showerror("Помилка", f"Не вдалося створити новий акаунт. {response.json()}")
                return False
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит не виконано: {e}")
            return False

    def create_widgets(self):
        self.header_label = tk.Label(self.root, text="Нотатки", font=("Helvetica", 18, "bold"))
        self.header_label.pack(pady=10)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var, font=("Helvetica", 14))
        self.search_entry.pack(pady=5)

        self.refresh_button = ttk.Button(self.root, text="Оновити", command=self.load_notes)
        self.refresh_button.pack(pady=5)

        self.notes_listbox = tk.Listbox(self.root, font=("Helvetica", 12), height=15)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        self.save_button = ttk.Button(self.root, text="Зберегти нотатку", command=self.save_note)
        self.save_button.pack(pady=5)
        self.delete_button = ttk.Button(self.root, text="Видалити нотатку", command=self.delete_note)
        self.delete_button.pack(pady=5)

    def fetch_access_token(self):
        try:
            response = requests.post("https://api.walletellaw.store/generate-token-desktop", json={"id": self.user_id})
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                self.load_notes()
            else:
                messagebox.showerror("Помилка", f"Не вдалося отримати токен доступу. {response.json()}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит не виконано: {e}")

    def load_notes(self):
        if not self.access_token:
            messagebox.showerror("Помилка", "Токен доступу не отриманий.")
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.post("https://api.walletellaw.store/getuseraccount", json={"id": self.user_id}, headers=headers)
            if response.status_code == 200:
                self.notes = response.json().get("notes", [])
                self.display_notes()
            else:
                messagebox.showerror("Помилка", f"Не вдалося отримати дані нотаток. {response.json()}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит не виконано: {e}")

    def display_notes(self):
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            note_title = note["header"] if note["header"] else "Без заголовку"

            try:
                note_date = parse_iso_datetime(note["created_at"]).strftime("%Y-%m-%d %H:%M")
            except ValueError as e:
                messagebox.showerror("Помилка", f"Неправильний формат дати: {e}")
                note_date = "Невідома дата"

            self.notes_listbox.insert(tk.END, f"{note_title} - {note_date}")

    def on_note_select(self, event):
        selected_index = self.notes_listbox.curselection()
        if selected_index:
            self.selected_note = self.notes[selected_index[0]]
            self.open_note_details(self.selected_note)

    def open_note_details(self, note):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Деталі нотатки")

        tk.Label(detail_window, text="Заголовок", font=("Helvetica", 12, "bold")).pack()
        header_entry = ttk.Entry(detail_window, font=("Helvetica", 12))
        header_entry.insert(0, note["header"])
        header_entry.pack(pady=5)

        tk.Label(detail_window, text="Текст", font=("Helvetica", 12, "bold")).pack()
        text_entry = tk.Text(detail_window, font=("Helvetica", 12), height=10)
        text_entry.insert(tk.END, note["text"])
        text_entry.pack(pady=5)

        def save_changes():
            note["header"] = header_entry.get()
            note["text"] = text_entry.get("1.0", tk.END).strip()
            self.save_note()
            detail_window.destroy()

        save_button = ttk.Button(detail_window, text="Зберегти", command=save_changes)
        save_button.pack(pady=5)

    def save_note(self):
        if not self.selected_note:
            messagebox.showerror("Помилка", "Нотатку не обрано.")
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.post("https://api.walletellaw.store/save-note", json=self.selected_note,
                                     headers=headers)
            if response.status_code == 200:
                self.load_notes()
            else:
                messagebox.showerror("Помилка", "Не вдалося зберегти нотатку.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит не виконано: {e}")

    def delete_note(self):
        if not self.selected_note:
            messagebox.showerror("Помилка", "Нотатку не обрано.")
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.post("https://api.walletellaw.store/delete-note", json={"id": self.selected_note["id"], "user_id": self.user_id},
                                     headers=headers)
            if response.status_code == 200:
                self.load_notes()
            else:
                messagebox.showerror("Помилка", "Не вдалося видалити нотатку.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Запит на видалення не виконано: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
