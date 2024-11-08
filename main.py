import tkinter as tk
from tkinter import messagebox
from db import add_user, add_note, get_notes, update_note
import os


class PersonalDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Особистий щоденник")
        self.root.geometry("400x400")
        self.root.config(bg="#2E2E2E")
        self.user_id_file = "user_id.txt"
        self.user_id = None
        self.selected_note_id = None

        if os.path.exists(self.user_id_file):
            self.load_user_id()
            self.show_notes_ui()
        else:
            self.show_registration_ui()

    def load_user_id(self):
        """Завантажує user_id з файлу."""
        with open(self.user_id_file, "r") as file:
            self.user_id = int(file.read().strip())

    def save_user_id(self, user_id):
        """Зберігає user_id у файл."""
        with open(self.user_id_file, "w") as file:
            file.write(str(user_id))

    def show_registration_ui(self):
        """Інтерфейс для реєстрації користувача."""
        self.clear_screen()

        label = tk.Label(self.root, text="Введіть ваше ім'я користувача:", font=("Arial", 14), bg="#2E2E2E", fg="white")
        label.pack(pady=(20, 10))

        self.username_entry = tk.Entry(self.root, width=30, font=("Arial", 12), bg="#3E3E3E", fg="white")
        self.username_entry.pack(pady=10, padx=20)

        create_button = tk.Button(self.root, text="Створити акаунт", command=self.register_user, font=("Arial", 12),
                                  bg="#4CAF50", fg="white", activebackground="#45A049")
        create_button.pack(pady=20)

    def register_user(self):
        """Реєструє нового користувача та зберігає його ID."""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Помилка", "Введіть ім'я користувача.")
            return

        user_id = add_user(username)
        if user_id:
            self.user_id = user_id
            self.save_user_id(self.user_id)
            self.show_notes_ui()
        else:
            messagebox.showerror("Помилка", "Не вдалося створити користувача.")

    def show_notes_ui(self):
        """Головний інтерфейс для перегляду всіх нотаток."""
        self.clear_screen()

        title_label = tk.Label(self.root, text="Ваші нотатки", font=("Arial", 18, "bold"), bg="#2E2E2E", fg="white")
        title_label.pack(pady=10)

        canvas = tk.Canvas(self.root, bg="#2E2E2E", highlightthickness=0, width=380)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Контейнер для нотаток всередині Canvas
        self.notes_container = tk.Frame(canvas, bg="#2E2E2E")
        self.notes_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.notes_container, anchor="nw")
        add_button = tk.Button(self.root, text="+", command=self.show_add_note_ui, font=("Arial", 14, "bold"),
                               bg="#4CAF50", fg="white", activebackground="#45A049", width=3)
        add_button.place(relx=0.9, rely=0.05)
        self.load_notes()

    def load_notes(self):
        """Завантажує нотатки користувача у вигляді блоків із заголовками."""
        # Очищуємо попередні нотатки з контейнера
        for widget in self.notes_container.winfo_children():
            widget.destroy()

        notes = get_notes(self.user_id)
        for note in notes:
            # Створюємо блок для кожного заголовка нотатки з бордером
            note_frame = tk.Frame(self.notes_container, bg="#3E3E3E", bd=2, relief="solid")
            note_frame.pack(fill=tk.X, pady=5, padx=5)

            # Додаємо заголовок нотатки
            title_label = tk.Label(note_frame, text=note[1], font=("Arial", 14, "bold"), bg="#3E3E3E", fg="white",
                                   anchor="w", padx=10, pady=5)
            title_label.pack(fill=tk.X)

            # Подія на клік для перегляду повної нотатки
            note_frame.bind("<Button-1>", lambda e, note_id=note[0]: self.open_note_by_id(note_id))
            title_label.bind("<Button-1>", lambda e, note_id=note[0]: self.open_note_by_id(note_id))

    def open_note_by_id(self, note_id):
        """Відкриває вибрану нотатку для перегляду та редагування за ID."""
        self.selected_note_id = note_id
        self.show_edit_note_ui()

    def show_add_note_ui(self):
        """Інтерфейс для створення нової нотатки."""
        self.selected_note_id = None
        self.show_edit_note_ui()

    def show_edit_note_ui(self):
        """Інтерфейс для перегляду або редагування вибраної нотатки."""
        self.clear_screen()

        back_button = tk.Button(self.root, text="← Назад", command=self.show_notes_ui, font=("Arial", 12), bg="#555555",
                                fg="white", activebackground="#777777")
        back_button.pack(anchor="nw", padx=10, pady=(10, 0))

        tk.Label(self.root, text="Заголовок:", font=("Arial", 14), bg="#2E2E2E", fg="white").pack(pady=5)
        self.title_entry = tk.Entry(self.root, font=("Arial", 12), width=30, bg="#3E3E3E", fg="white")
        self.title_entry.pack(pady=5, padx=20)

        tk.Label(self.root, text="Текст:", font=("Arial", 14), bg="#2E2E2E", fg="white").pack(pady=5)
        self.memo_text = tk.Text(self.root, font=("Arial", 12), width=30, height=10, bg="#3E3E3E", fg="white")
        self.memo_text.pack(pady=5, padx=20)

        if self.selected_note_id:
            notes = get_notes(self.user_id)
            for note in notes:
                if note[0] == self.selected_note_id:
                    self.title_entry.insert(0, note[1])
                    self.memo_text.insert("1.0", note[2])

        save_button = tk.Button(self.root, text="Зберегти", command=self.save_note, font=("Arial", 12), bg="#4CAF50",
                                fg="white", activebackground="#45A049")
        save_button.pack(pady=10)

    def save_note(self):
        """Зберігає нову або оновлює існуючу нотатку."""
        title = self.title_entry.get()
        content = self.memo_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Помилка", "Введіть заголовок та текст нотатки.")
            return

        if self.selected_note_id:
            update_note(self.selected_note_id, title, content)
        else:
            add_note(self.user_id, title, content)

        self.show_notes_ui()

    def clear_screen(self):
        """Очищує всі віджети з екрана."""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalDiaryApp(root)
    root.mainloop()
