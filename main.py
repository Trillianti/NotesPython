import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import platform


def parse_iso_datetime(date_str):
    return datetime.fromisoformat(date_str)


def current_iso_datetime():
    return datetime.now().isoformat()


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Нотатки")
        self.root.geometry("600x700")
        self.root.configure(bg="#1d1e26")

        self.notes_file = "notes.json"
        self.notes = []
        self.filtered_notes = []
        self.selected_note = None
        self.search_query = ""

        self.create_widgets()
        self.load_notes()

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#1d1e26")
        header_frame.pack(fill=tk.X, pady=10)

        self.header_label = tk.Label(
            header_frame, text="Нотатки", font=("Helvetica", 24, "bold"), bg="#1d1e26", fg="#ffffff"
        )
        self.header_label.pack(side=tk.LEFT, padx=20)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.update_search_query())
        self.search_entry = ttk.Entry(header_frame, textvariable=self.search_var, font=("Helvetica", 14))
        self.search_entry.pack(side=tk.RIGHT, padx=20, pady=5)

        notes_frame = tk.Frame(self.root, bg="#1d1e26")
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)  # Додаємо відступи зліва і справа

        self.notes_canvas = tk.Canvas(notes_frame, bg="#1d1e26", highlightthickness=0)
        self.notes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.notes_frame = tk.Frame(self.notes_canvas, bg="#1d1e26")
        self.notes_canvas.create_window((0, 0), window=self.notes_frame, anchor="nw")

        self.notes_frame.bind(
            "<Configure>", lambda e: self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all"))
        )

        system_platform = platform.system()
        if system_platform == 'Windows':
            self.notes_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        elif system_platform == 'Darwin':  # macOS
            self.notes_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:  # Linux
            self.notes_canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
            self.notes_canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

        add_button = tk.Button(
            self.root,
            text="+",
            font=("Helvetica", 18, "bold"),
            bg="#2ecc71",
            fg="#ffffff",
            command=self.add_note,
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        add_button.place(relx=0.9, rely=0.9, anchor="center", width=60, height=60)

    def _on_mousewheel(self, event):
        self.notes_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.notes_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.notes_canvas.yview_scroll(1, "units")

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r") as file:
                self.notes = json.load(file)
        else:
            self.notes = []
        self.filtered_notes = self.notes.copy()
        self.categorize_notes()

    def save_notes_to_file(self):
        with open(self.notes_file, "w") as file:
            json.dump(self.notes, file, indent=4)

    def update_search_query(self):
        self.search_query = self.search_var.get().strip().lower()
        self.categorize_notes()

    def categorize_notes(self):
        today = datetime.now()
        today_notes = []
        last7_days_notes = []
        last30_days_notes = []
        monthly_notes = {}

        filtered_notes = [
            note for note in self.notes
            if self.search_query in (note["header"] or "Без заголовку").lower()
        ]

        filtered_notes = sorted(filtered_notes, key=lambda x: parse_iso_datetime(x["created_at"]), reverse=True)

        for note in filtered_notes:
            note_date = parse_iso_datetime(note["created_at"])

            if note_date.date() == today.date():
                today_notes.append(note)
            elif today - timedelta(days=7) <= note_date:
                last7_days_notes.append(note)
            elif today - timedelta(days=30) <= note_date:
                last30_days_notes.append(note)
            else:
                month_year = note_date.strftime("%B %Y")
                if month_year not in monthly_notes:
                    monthly_notes[month_year] = []
                monthly_notes[month_year].append(note)

        self.display_notes(today_notes, last7_days_notes, last30_days_notes, monthly_notes)



    def display_notes(self, today_notes, last7_days_notes, last30_days_notes, monthly_notes):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        self.add_category("Сьогодні", today_notes)
        self.add_category("За останні 7 днів", last7_days_notes)
        self.add_category("За останні 30 днів", last30_days_notes)

        for month_year, notes in monthly_notes.items():
            self.add_category(month_year, notes)

    def add_category(self, title, notes):
        if notes:
            section_label = tk.Label(
                self.notes_frame,
                text=title,
                font=("Helvetica", 18, "bold"),
                bg="#1d1e26",
                fg="#ffffff",
            )
            section_label.pack(anchor="w", pady=(10, 5))

            for note in notes:
                self.create_note_item(note)

    def create_note_item(self, note):
        actual_header = (note["header"][:20] + "...") if len(note["header"]) > 20 else note["header"] or "Без заголовку"

        frame = tk.Frame(self.notes_frame, bg="#2c2f38", pady=5, padx=5)
        frame.pack(fill=tk.X, expand=True, pady=5)

        title_label = tk.Label(
            frame,
            text=actual_header,
            font=("Helvetica", 14),
            bg="#2c2f38",
            fg="#ffffff",
            anchor="w",
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        timestamp_label = tk.Label(
            frame,
            text=parse_iso_datetime(note["created_at"]).strftime("%Y-%m-%d %H:%M"),
            font=("Helvetica", 12),
            bg="#2c2f38",
            fg="#888888",
            anchor="e",
        )
        timestamp_label.pack(side=tk.RIGHT, padx=10)

        def on_click(event):
            self.open_note_by_id(note["id"])

        frame.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)
        timestamp_label.bind("<Button-1>", on_click)

    def open_note_by_id(self, note_id):
        note = next((n for n in self.notes if n["id"] == note_id), None)
        if note:
            self.open_note_details(note)
        else:
            messagebox.showerror("Помилка", f"Нотатка з id={note_id} не знайдена.")

    def add_note(self):
        new_id = max([note["id"] for note in self.notes], default=0) + 1
        new_note = {
            "id": new_id,
            "header": "",
            "text": "",
            "created_at": current_iso_datetime(),
            "updated_at": current_iso_datetime(),
        }
        self.notes.append(new_note)
        self.save_notes_to_file()
        self.open_note_details(new_note)

    def open_note_details(self, note):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Редагувати нотатку")
        detail_window.geometry("400x400")
        detail_window.configure(bg="#1d1e26")

        tk.Label(detail_window, text="Заголовок:", font=("Helvetica", 12, "bold"),
                 bg="#1d1e26", fg="#ffffff").pack(pady=5)
        header_entry = ttk.Entry(detail_window, font=("Helvetica", 12))
        header_entry.insert(0, note["header"])
        header_entry.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(detail_window, text="Текст:", font=("Helvetica", 12, "bold"),
                 bg="#1d1e26", fg="#ffffff").pack(pady=5)
        text_entry = tk.Text(detail_window, font=("Helvetica", 12), height=10, wrap=tk.WORD)
        text_entry.insert(tk.END, note["text"])
        text_entry.pack(fill=tk.BOTH, padx=20, pady=5, expand=True)

        def save_changes():
            header = header_entry.get().strip()
            text = text_entry.get("1.0", tk.END).strip()

            if not header and not text:
                if messagebox.askyesno("Видалити нотатку", "Нотатка порожня. Видалити її?"):
                    self.notes = [n for n in self.notes if n["id"] != note["id"]]
                    self.save_notes_to_file()
                    self.categorize_notes()
                detail_window.destroy()
                return

            note["header"] = header
            note["text"] = text
            note["updated_at"] = current_iso_datetime()
            self.save_notes_to_file()
            self.categorize_notes()
            detail_window.destroy()

        def delete_note():
            if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити цю нотатку?"):
                self.notes = [n for n in self.notes if n["id"] != note["id"]]
                self.save_notes_to_file()
                self.categorize_notes()
                detail_window.destroy()

        ttk.Button(detail_window, text="Зберегти", command=save_changes).pack(pady=10)
        ttk.Button(detail_window, text="Видалити", command=delete_note).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
