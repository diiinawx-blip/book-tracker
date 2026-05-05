import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x500")
        
        # Путь к файлу данных
        self.data_file = "books.json"
        self.books = [] # Список для хранения книг в памяти

        # --- Создание виджетов ---
        self.create_widgets()
        
        # Загрузка данных из файла при запуске
        self.load_from_json()
        
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить новую книгу", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=40)
        self.author_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = ttk.Entry(input_frame, width=40)
        self.genre_entry.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(input_frame, text="Страниц:").grid(row=2, column=2, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=2, column=3, sticky="e", pady=2)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить книгу", command=self.add_book).grid(
            row=3, column=0, columnspan=4, pady=10, sticky="ew"
        )

        # Таблица для отображения книг
        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        # Фильтрация по жанру
        filter_frame = ttk.Frame(self.root)
        filter_frame.grid(row=2, column=0, sticky="ew", padx=10)
        
        ttk.Label(filter_frame, text="Фильтр по жанру:").pack(side="left")
        
        # Получаем уникальные жанры для выпадающего списка
        genres = sorted({book['genre'] for book in self.books})
        self.genre_var = tk.StringVar(value=genres[0] if genres else "")
        
        self.genre_combo = ttk.Combobox(filter_frame, textvariable=self.genre_var, 
                                       values=genres, state="readonly", width=25)
        self.genre_combo.pack(side="left", padx=(5, 0))
        
        ttk.Button(filter_frame, text="Фильтровать", command=self.filter_by_genre).pack(side="left", padx=(5, 0))

        # Фильтрация по страницам
        pages_frame = ttk.Frame(self.root)
        pages_frame.grid(row=2, column=1, sticky="e")
        
        ttk.Label(pages_frame, text="Страниц >").pack(side="left")
        
        self.pages_filter_var = tk.StringVar()
        self.pages_filter_entry = ttk.Entry(pages_frame, textvariable=self.pages_filter_var, width=8)
        self.pages_filter_entry.pack(side="left", padx=(5, 0))
        
        ttk.Button(pages_frame, text="Фильтровать", command=self.filter_by_pages).pack(side="left", padx=(5, 0))

    def add_book(self):
        """Добавляет книгу в список после проверки данных."""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

         # Валидация ввода
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        if not pages_str.isdigit() or int(pages_str) <= 0:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        pages = int(pages_str)
         
         # Добавление в список и таблицу
        book = {"title": title, "author": author, "genre": genre, "pages": pages}
        self.books.append(book)
        self.update_treeview()
         
         # Очистка полей и сохранение
        self.clear_entries()
        self.save_to_json()

    def clear_entries(self):
         """Очищает поля ввода."""
         self.title_entry.delete(0, tk.END)
         self.author_entry.delete(0, tk.END)
         self.genre_entry.delete(0, tk.END)
         self.pages_entry.delete(0, tk.END)
         self.title_entry.focus()

    def update_treeview(self):
         """Обновляет данные в таблице."""
         for i in self.tree.get_children():
             self.tree.delete(i)
             
         for book in self.books:
             self.tree.insert("", tk.END, values=(book['title'], book['author'], book['genre'], book['pages']))
         
         # Обновление списка жанров в фильтре
         genres = sorted({book['genre'] for book in self.books})
         self.genre_combo['values'] = genres
         if genres:
             self.genre_var.set(genres[0])

    def filter_by_genre(self):
         """Фильтрует книги по выбранному жанру."""
         selected_genre = self.genre_var.get()
         
         if not selected_genre:
             filtered_books = self.books
         else:
             filtered_books = [book for book in self.books if book['genre'] == selected_genre]
             
         self.display_books(filtered_books)

    def filter_by_pages(self):
         """Фильтрует книги по количеству страниц."""
         pages_str = self.pages_filter_var.get()
         
         if not pages_str.isdigit():
             messagebox.showerror("Ошибка", "Введите число для фильтрации страниц!")
             return

         min_pages = int(pages_str)
         filtered_books = [book for book in self.books if book['pages'] > min_pages]
         
         self.display_books(filtered_books)

    def display_books(self, books_to_display):
         """Отображает переданный список книг в таблице."""
         for i in self.tree.get_children():
             self.tree.delete(i)
             
         for book in books_to_display:
             self.tree.insert("", tk.END, values=(book['title'], book['author'], book['genre'], book['pages']))

    def save_to_json(self):
         """Сохраняет список книг в файл JSON."""
         try:
             with open(self.data_file, 'w', encoding='utf-8') as f:
                 json.dump(self.books, f, ensure_ascii=False, indent=4)
             print(f"Данные сохранены в {self.data_file}")
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def load_from_json(self):
         """Загружает книги из файла JSON при запуске."""
         if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                      self.books = json.load(f)
                      print(f"Данные загружены из {self.data_file}")
            except Exception as e:
                  messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
                  self.books = []
            else:
              print(f"Файл {self.data_file} не найден. Будет создан новый.")
              self.books = []
          # Отобразить загруженные данные
            self.update_treeview()


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    
    # Настройка весов для растягивания таблицы
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    root.mainloop()