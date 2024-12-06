import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
import csv
import re

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    cursor.executescript('''
        -- Таблица "Кандидаты"
        CREATE TABLE IF NOT EXISTS Candidate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            skills TEXT,
            experience TEXT
        );
         -- Таблица "Вакансии"
        CREATE TABLE IF NOT EXISTS Vacancy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            requirements TEXT,
            salary REAL,
            employer_id INTEGER,
            FOREIGN KEY(employer_id) REFERENCES Employer(id) ON DELETE CASCADE
        );
        
        -- Таблица "Наниматели"
        CREATE TABLE IF NOT EXISTS Employer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT
        );
        
        -- Таблица "Резюме"
        CREATE TABLE IF NOT EXISTS Resume (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            vacancy_id INTEGER,
            skills TEXT,
            creation_date TEXT,
            FOREIGN KEY(candidate_id) REFERENCES Candidate(id)
            FOREIGN KEY(vacancy_id) REFERENCES Vacancy(id)
        );

        -- Таблица "Собеседования"
        CREATE TABLE IF NOT EXISTS Interview (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER,
            candidate_id INTEGER,
            employer_id INTEGER, 
            date_time TEXT,
            result TEXT,
            FOREIGN KEY(vacancy_id) REFERENCES Vacancy(id),
            FOREIGN KEY(candidate_id) REFERENCES Candidate(id),
            FOREIGN KEY(employer_id) REFERENCES Employer(id) 
        );
    ''')

    # Функция для проверки, есть ли данные в таблице
    def is_table_empty(table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] == 0

    # Добавляем тестовые данные только если таблица пуста
    if is_table_empty("Candidate"):
        cursor.executemany('''
            INSERT INTO Candidate (name, contact, skills, experience)
            VALUES (?, ?, ?, ?)
        ''', [
            ("Иван Иванов", "ivan@example.com", "Python, SQL", "5 лет"),
            ("Анна Смирнова", "anna@example.com", "Java, Spring", "3 года"),
            ("Петр Петров", "petr@example.com", "JavaScript, React", "2 года"),
        ])

    if is_table_empty("Employer"):
        cursor.executemany('''
            INSERT INTO Employer (company_name, contact_person, phone, email)
            VALUES (?, ?, ?, ?)
        ''', [
            ("ООО ТехСофт", "Сергей Кузнецов", "+7-123-456-7890", "sergey@techsoft.ru"),
            ("ЗАО Инновации", "Ольга Лебедева", "+7-987-654-3210", "olga@innovations.com"),
        ])

    if is_table_empty("Vacancy"):
        cursor.executemany('''
            INSERT INTO Vacancy (title, description, requirements, salary, employer_id)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ("Разработчик Python", "Разработка backend-систем", "Python, Django", 120000, 1),
            ("Frontend-разработчик", "Разработка UI", "HTML, CSS, React", 100000, 1),
            ("Java-разработчик", "Работа с корпоративными системами", "Java, Spring", 130000, 2),
        ])

    if is_table_empty("Resume"):
        cursor.executemany('''
            INSERT INTO Resume (candidate_id, vacancy_id, skills, creation_date)
            VALUES (?, ?, ?, ?)
        ''', [
            (1, 1, "Python, SQL", "2024-12-01"),
            (2, 3, "Java, Spring", "2024-12-02"),
            (3, 2, "JavaScript, React", "2024-12-03"),
        ])

    if is_table_empty("Interview"):
        cursor.executemany('''
            INSERT INTO Interview (vacancy_id, candidate_id, employer_id, date_time, result)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 1, 1, "2024-12-05 10:00", "Успешно"),
            (3, 2, 2, "2024-12-06 14:00", "Ожидает решения"),
            (2, 3, 1, "2024-12-07 16:00", "Отказ"),
        ])

    print("База данных успешно заполнена тестовыми данными!")
    conn.commit()
    conn.close()
# Главный интерфейс
root = Tk()
root.title("АРМ Рекрутинговое агентство")
root.geometry("1000x600")

# Вкладки
tab_control = ttk.Notebook(root)
tab_candidates = Frame(tab_control)
tab_vacancies = Frame(tab_control)
tab_employers = Frame(tab_control)
tab_resumes = Frame(tab_control)
tab_interviews = Frame(tab_control)

tab_control.add(tab_candidates, text="Кандидаты")
tab_control.add(tab_vacancies, text="Вакансии")
tab_control.add(tab_employers, text="Наниматели")
tab_control.add(tab_resumes, text="Резюме")
tab_control.add(tab_interviews, text="Собеседования")
tab_control.pack(expand=1, fill="both")

# Функции для работы с базой данных
def add_candidate():
    def save_candidate():
        name = name_var.get()
        contact = contact_var.get()
        skills = skills_text.get("1.0", "end-1c").strip()
        experience = experience_text.get("1.0", "end-1c").strip()

        # Проверка имени
        if not name:
            messagebox.showerror("Ошибка", "Имя кандидата обязательно!")
            return


        # Проверка навыков и опыта
        if not skills:
            messagebox.showerror("Ошибка", "Поле 'Навыки' не должно быть пустым!")
            return
        if not experience:
            messagebox.showerror("Ошибка", "Поле 'Опыт' не должно быть пустым!")
            return

        # Сохранение данных в базу
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Candidate (name, contact, skills, experience) VALUES (?, ?, ?, ?)",
            (name, contact, skills, experience)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Кандидат добавлен!")
        add_window.destroy()
        refresh_candidates()

    add_window = Toplevel(root)
    add_window.title("Добавить кандидата")
    add_window.geometry("400x400")

    Label(add_window, text="Имя").pack(pady=5)
    name_var = StringVar()
    Entry(add_window, textvariable=name_var).pack()

    Label(add_window, text="Контакты").pack(pady=5)
    contact_var = StringVar()
    Entry(add_window, textvariable=contact_var).pack()

    Label(add_window, text="Навыки").pack(pady=5)
    skills_text = Text(add_window, width=20, height=5, wrap="word")
    skills_text.pack()

    Label(add_window, text="Опыт").pack(pady=5)
    experience_text = Text(add_window, width=20, height=5, wrap="word")
    experience_text.pack()

    Button(add_window, text="Сохранить", command=save_candidate).pack(pady=10)


# Обновление списка кандидатов
def refresh_candidates(search_query=None, column=None):
    for row in tree_candidates.get_children():
        tree_candidates.delete(row)

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    base_query = """
        SELECT id, name, contact, skills, experience FROM Candidate
    """

    # Словарь для сопоставления колонок в интерфейсе с реальными именами в БД
    columns_map = {
        "Имя": "name",
        "Контакты": "contact",
        "Навыки": "skills",
        "Опыт": "experience"
    }

    # Если есть поисковый запрос и выбранная колонка
    if search_query and column in columns_map:
        search_query = f"%{search_query}%"
        base_query += f" WHERE {columns_map[column]} LIKE ?"
        cursor.execute(base_query, (search_query,))
    else:
        cursor.execute(base_query)

    # Заполняем таблицу новыми данными
    for row in cursor.fetchall():
        tree_candidates.insert("", END, values=row)
    conn.close()



# Удаление кандидата
def delete_candidate():
    selected_item = tree_candidates.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите кандидата для удаления!")
        return

    candidate_id = tree_candidates.item(selected_item, "values")[0]

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Candidate WHERE id=?", (candidate_id,))
    conn.commit()
    conn.close()
    refresh_candidates()
    messagebox.showinfo("Успех", "Кандидат удален!")

# Изменение данных кандидата
def edit_candidate():
    selected_item = tree_candidates.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите кандидата для редактирования!")
        return

    candidate_id = tree_candidates.item(selected_item, "values")[0]

    def save_changes():
        new_name = name_var.get()
        new_contact = contact_var.get()
        new_skills = skills_text.get("1.0", "end-1c").strip()
        new_experience = experience_text.get("1.0", "end-1c").strip()

        # Проверки
        if not new_name:
            messagebox.showerror("Ошибка", "Имя кандидата обязательно!")
            return

        # Обновление в базе данных
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Candidate SET name=?, contact=?, skills=?, experience=? WHERE id=?",
            (new_name, new_contact, new_skills, new_experience, candidate_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Данные кандидата обновлены!")
        edit_window.destroy()
        refresh_candidates()

    # Окно редактирования
    edit_window = Toplevel(root)
    edit_window.title("Редактировать кандидата")
    edit_window.geometry("400x400")

    # Текущие данные кандидата
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, contact, skills, experience FROM Candidate WHERE id=?", (candidate_id,))
    current_data = cursor.fetchone()
    conn.close()

    # Поля для редактирования
    Label(edit_window, text="Имя").pack(pady=5)
    name_var = StringVar(value=current_data[0])
    Entry(edit_window, textvariable=name_var).pack()

    Label(edit_window, text="Контакты").pack(pady=5)
    contact_var = StringVar(value=current_data[1])
    Entry(edit_window, textvariable=contact_var).pack()

    Label(edit_window, text="Навыки").pack(pady=5)
    skills_text = Text(edit_window, width=20, height=5, wrap="word")
    skills_text.insert("1.0", current_data[2])
    skills_text.pack()

    Label(edit_window, text="Опыт").pack(pady=5)
    experience_text = Text(edit_window, width=20, height=5, wrap="word")
    experience_text.insert("1.0", current_data[3])
    experience_text.pack()

    # Кнопки
    Button(edit_window, text="Сохранить изменения", command=save_changes).pack(pady=10)
    Button(edit_window, text="Отменить", command=edit_window.destroy).pack(pady=5)


tree_candidates = ttk.Treeview(tab_candidates, columns=("id", "name", "contact", "skills", "experience"), show="headings")

def generate_report():
    # Подключаемся к базе данных
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    # Извлекаем данные из таблицы Candidate
    cursor.execute("SELECT id, name, contact, skills, experience FROM Candidate")
    candidates_data = cursor.fetchall()
    conn.close()

    if not candidates_data:
        messagebox.showerror("Ошибка", "Нет данных для создания отчета!")
        return

    # Сохраняем данные в CSV файл
    with open('candidates_report.txt', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Записываем заголовки
        writer.writerow(["ID", "Имя", "Контакты", "Навыки", "Опыт"])
        # Записываем строки с данными
        writer.writerows(candidates_data)

    messagebox.showinfo("Успех", "Отчет по кандидатам создан и сохранен в 'candidates_report.txt'!")

# Таблица кандидатов
tree_candidates.heading("id", text="ID")
tree_candidates.heading("name", text="Имя")
tree_candidates.heading("contact", text="Контакты")
tree_candidates.heading("skills", text="Навыки")
tree_candidates.heading("experience", text="Опыт")
tree_candidates.pack(expand=1, fill="both")

# Фрейм для элементов поиска кандидатов
search_frame_candidates = Frame(tab_candidates)
search_frame_candidates.pack(fill="x", padx=10, pady=5)

# Метка и поле для ввода текста
Label(search_frame_candidates, text="Поиск:").pack(side=LEFT, padx=5)

search_var_candidates = StringVar()
Entry(search_frame_candidates, textvariable=search_var_candidates).pack(side=LEFT, fill="x", expand=True, padx=5)

# Выпадающий список для выбора колонки
Label(search_frame_candidates, text="В колонке:").pack(side=LEFT, padx=5)

column_var_candidates = StringVar()
column_var_candidates.set("Имя")  # Устанавливаем значение по умолчанию
OptionMenu(search_frame_candidates, column_var_candidates, "Имя", "Контакты", "Навыки", "Опыт").pack(side=LEFT, padx=5)

# Кнопки для управления кандидатами
frame_candidates = Frame(tab_candidates)
frame_candidates.pack(pady=10)
Button(frame_candidates, text="Добавить кандидата", command=add_candidate).pack(side=LEFT, padx=5)
Button(frame_candidates, text="Удалить кандидата", command=delete_candidate).pack(side=LEFT, padx=5)
Button(frame_candidates, text="Изменить кандидата", command=edit_candidate).pack(side=LEFT, padx=5)
Button(frame_candidates, text="Создать отчет", command=generate_report).pack(side=LEFT, padx=15)

# Кнопка поиска
search_button_candidates = Button(
    search_frame_candidates,
    text="Искать",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_candidates(search_var_candidates.get(), column_var_candidates.get())
)
search_button_candidates.pack(side=LEFT, padx=5)

# Кнопка сброса фильтра
reset_button_candidates = Button(
    search_frame_candidates,
    text="Сбросить фильтр",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_candidates()
)
reset_button_candidates.pack(side=LEFT, padx=5)

# Функции для работы с вакансиями
def add_vacancy():
    def save_vacancy():
        title = title_var.get()
        description = description_text.get("1.0", "end-1c")
        requirements = requirements_text.get("1.0", "end-1c")
        salary = salary_var.get()
        employer_id = employer_id_var.get().split(" - ")[0]  # Извлекаем только ID нанимателя

        if not title:
            messagebox.showerror("Ошибка", "Название вакансии обязательно!")
            return

        try:
            salary_value = float(salary) if salary else None
        except ValueError:
            messagebox.showerror("Ошибка", "Зарплата должна быть числом!")
            return

        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Vacancy (title, description, requirements, salary, employer_id) VALUES (?, ?, ?, ?, ?)",
            (title, description, requirements, salary_value, employer_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Вакансия добавлена!")
        add_window.destroy()
        refresh_vacancies()

    add_window = Toplevel(root)
    add_window.title("Добавить вакансию")
    add_window.geometry("400x450")

    Label(add_window, text="Название вакансии").pack(pady=5)
    title_var = StringVar()
    Entry(add_window, textvariable=title_var).pack()

    Label(add_window, text="Описание").pack(pady=5)
    description_text = Text(add_window, width=20, height=5, wrap="word")
    description_text.pack()

    Label(add_window, text="Требования").pack(pady=5)
    requirements_text = Text(add_window, width=20, height=5, wrap="word")
    requirements_text.pack()

    Label(add_window, text="Зарплата").pack(pady=5)
    salary_var = StringVar()
    Entry(add_window, textvariable=salary_var).pack()

    # Выпадающий список для выбора нанимателя
    Label(add_window, text="Наниматель").pack(pady=5)
    employer_id_var = StringVar()
    employer_dropdown = ttk.Combobox(add_window, textvariable=employer_id_var)
    employer_dropdown.pack()

    # Получение списка нанимателей из базы данных
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name FROM Employer")
    employers = cursor.fetchall()
    conn.close()

    # Настройка выпадающего списка
    employer_dropdown['values'] = [f"{employer[0]} - {employer[1]}" for employer in employers]
    if employers:
        employer_dropdown.current(0)  # Установить первый элемент по умолчанию

    Button(add_window, text="Сохранить", command=save_vacancy).pack(pady=10)

# Обновление списка вакансий
# Обновление списка вакансий с учетом поиска и фильтрации
def refresh_vacancies(search_query=None, column=None):
    for row in tree_vacancies.get_children():
        tree_vacancies.delete(row)

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    base_query = """
        SELECT Vacancy.id, Vacancy.title, Vacancy.description, Vacancy.requirements, Vacancy.salary, Employer.company_name
        FROM Vacancy
        LEFT JOIN Employer ON Vacancy.employer_id = Employer.id
    """

    # Словарь для сопоставления колонок в интерфейсе с реальными именами в БД
    columns_map = {
        "Название": "title",
        "Описание": "description",
        "Требования": "requirements",
        "Зарплата": "salary",
        "Наниматель": "Employer.company_name"
    }

    # Если есть поисковый запрос и выбранная колонка
    if search_query and column in columns_map:
        search_query = f"%{search_query}%"
        base_query += f" WHERE {columns_map[column]} LIKE ?"
        cursor.execute(base_query, (search_query,))
    else:
        cursor.execute(base_query)

    # Заполняем таблицу новыми данными
    for row in cursor.fetchall():
        tree_vacancies.insert("", END, values=(row[0], row[1], row[2], row[3], row[4], row[5]))

    conn.close()


# Удаление вакансии
def delete_vacancy():
    selected_item = tree_vacancies.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите вакансию для удаления!")
        return

    vacancy_id = tree_vacancies.item(selected_item, "values")[0]

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Vacancy WHERE id=?", (vacancy_id,))
    conn.commit()
    conn.close()
    refresh_vacancies()
    messagebox.showinfo("Успех", "Вакансия удалена!")

# Изменение вакансии
def edit_vacancy():
    selected_item = tree_vacancies.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите вакансию для редактирования!")
        return

    vacancy_id = tree_vacancies.item(selected_item, "values")[0]

    def save_changes():
        title = title_var.get()
        description = description_text.get("1.0", "end-1c")
        requirements = requirements_text.get("1.0", "end-1c")
        salary = salary_var.get()
        employer_id = employer_id_var.get().split(" - ")[0]  # Извлекаем только ID нанимателя

        if not title:
            messagebox.showerror("Ошибка", "Название вакансии обязательно!")
            return

        try:
            salary_value = float(salary) if salary else None
        except ValueError:
            messagebox.showerror("Ошибка", "Зарплата должна быть числом!")
            return

        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Vacancy 
            SET title = ?, description = ?, requirements = ?, salary = ?, employer_id = ?
            WHERE id = ?
        """, (title, description, requirements, salary_value, employer_id, vacancy_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Изменения сохранены!")
        edit_window.destroy()
        refresh_vacancies()

    # Получение текущих данных вакансии
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, requirements, salary, employer_id 
        FROM Vacancy WHERE id = ?
    """, (vacancy_id,))
    vacancy_data = cursor.fetchone()
    conn.close()

    edit_window = Toplevel(root)
    edit_window.title("Редактировать вакансию")
    edit_window.geometry("400x450")

    Label(edit_window, text="Название вакансии").pack(pady=5)
    title_var = StringVar(value=vacancy_data[0])
    Entry(edit_window, textvariable=title_var).pack()

    Label(edit_window, text="Описание").pack(pady=5)
    description_text = Text(edit_window, width=20, height=5, wrap="word")
    description_text.insert("1.0", vacancy_data[1])
    description_text.pack()

    Label(edit_window, text="Требования").pack(pady=5)
    requirements_text = Text(edit_window, width=20, height=5, wrap="word")
    requirements_text.insert("1.0", vacancy_data[2])
    requirements_text.pack()

    Label(edit_window, text="Зарплата").pack(pady=5)
    salary_var = StringVar(value=str(vacancy_data[3]) if vacancy_data[3] else "")
    Entry(edit_window, textvariable=salary_var).pack()

    # Выпадающий список для выбора нанимателя
    Label(edit_window, text="Наниматель").pack(pady=5)
    employer_id_var = StringVar()
    employer_dropdown = ttk.Combobox(edit_window, textvariable=employer_id_var)
    employer_dropdown.pack()

    # Получение списка нанимателей из базы данных
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name FROM Employer")
    employers = cursor.fetchall()
    conn.close()

    employer_dropdown['values'] = [f"{employer[0]} - {employer[1]}" for employer in employers]
    current_employer = next(
        (f"{employer[0]} - {employer[1]}" for employer in employers if str(employer[0]) == str(vacancy_data[4])),
        ""
    )
    if current_employer:
        employer_dropdown.set(current_employer)

    Button(edit_window, text="Сохранить изменения", command=save_changes).pack(pady=10)
    Button(edit_window, text="Отменить", command=edit_window.destroy).pack(pady=5)


# Функция для создания отчета
def create_report():
    # Открываем файл для записи
    with open("vacancies_report.txt", "w", encoding="utf-8") as file:
        # Записываем заголовки
        file.write("ID\tНазвание\tОписание\tТребования\tЗарплата\tНаниматель\n")

        # Получаем все записи из таблицы и записываем их в файл
        for row in tree_vacancies.get_children():
            values = tree_vacancies.item(row, "values")
            file.write("\t".join(str(value) for value in values) + "\n")

    messagebox.showinfo("Отчет", "Отчет успешно создан и сохранен в файл 'vacancies_report.txt'!")

# Таблица вакансий
tree_vacancies = ttk.Treeview(tab_vacancies, columns=("id", "title","description","requirements","salary", "employer_id"), show="headings")
tree_vacancies.heading("id", text="ID")
tree_vacancies.heading("title", text="Название")
tree_vacancies.heading("description", text="Опиасние")
tree_vacancies.heading("requirements", text="Требования")
tree_vacancies.heading("salary", text="Зарплата")
tree_vacancies.heading("employer_id", text="Наниматель")
tree_vacancies.pack(expand=1, fill="both")

# Фрейм для элементов поиска вакансий
search_frame_vacancies = Frame(tab_vacancies)
search_frame_vacancies.pack(fill="x", padx=10, pady=5)

# Метка и поле для ввода текста
Label(search_frame_vacancies, text="Поиск:").pack(side=LEFT, padx=5)

search_var_vacancies = StringVar()
Entry(search_frame_vacancies, textvariable=search_var_vacancies).pack(side=LEFT, fill="x", expand=True, padx=5)

# Выпадающий список для выбора колонки
Label(search_frame_vacancies, text="В колонке:").pack(side=LEFT, padx=5)

column_var_vacancies = StringVar()
column_var_vacancies.set("Название")  # Устанавливаем значение по умолчанию
OptionMenu(search_frame_vacancies, column_var_vacancies, "Название", "Описание", "Требования", "Зарплата", "Наниматель").pack(side=LEFT, padx=5)

# Кнопки для управления вакансиями
frame_vacancies = Frame(tab_vacancies)
frame_vacancies.pack(pady=10)
Button(frame_vacancies, text="Добавить вакансию", command=add_vacancy).pack(side=LEFT, padx=15)
Button(frame_vacancies, text="Удалить вакансию", command=delete_vacancy).pack(side=LEFT, padx=5)
Button(frame_vacancies, text="Изменить вакансию", command=edit_vacancy).pack(side=LEFT, padx=5)
Button(frame_vacancies, text="Создать отчет", command=create_report).pack(side=LEFT, padx=15)


# Кнопка поиска
search_button_vacancies = Button(
    search_frame_vacancies,
    text="Искать",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_vacancies(search_var_vacancies.get(), column_var_vacancies.get())
)
search_button_vacancies.pack(side=LEFT, padx=5)

# Кнопка сброса фильтра
reset_button_vacancies = Button(
    search_frame_vacancies,
    text="Сбросить фильтр",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_vacancies()  # Сбросить фильтрацию
)
reset_button_vacancies.pack(side=LEFT, padx=5)


# Функции для работы с нанимателями

def add_employer():
    def save_employer():
        company_name = company_name_var.get()
        contact_person = contact_person_var.get()
        phone = phone_var.get()
        email = email_var.get()

        # Проверка названия компании
        if not company_name:
            messagebox.showerror("Ошибка", "Название компании обязательно!")
            return

        # Проверка телефона
        if not re.fullmatch(r"[+\-0-9]+", phone):
            messagebox.showerror("Ошибка", "Телефон может содержать только цифры, знаки '+' и '-'.")
            return

        # Проверка электронной почты
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Ошибка", "Введите корректный адрес электронной почты!")
            return

        # Сохранение данных в базу
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Employer (company_name, contact_person, phone, email) VALUES (?, ?, ?, ?)",
            (company_name, contact_person, phone, email)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Наниматель добавлен!")
        add_window.destroy()
        refresh_employers()

    add_window = Toplevel(root)
    add_window.title("Добавить нанимателя")
    add_window.geometry("400x300")

    Label(add_window, text="Название компании").pack(pady=5)
    company_name_var = StringVar()
    Entry(add_window, textvariable=company_name_var).pack()

    Label(add_window, text="Контактное лицо").pack(pady=5)
    contact_person_var = StringVar()
    Entry(add_window, textvariable=contact_person_var).pack()

    Label(add_window, text="Телефон").pack(pady=5)
    phone_var = StringVar()
    Entry(add_window, textvariable=phone_var).pack()

    Label(add_window, text="Email").pack(pady=5)
    email_var = StringVar()
    Entry(add_window, textvariable=email_var).pack()

    Button(add_window, text="Сохранить", command=save_employer).pack(pady=10)



# Обновление списка нанимателей
def refresh_employers(search_query=None, column=None):
    for row in tree_employers.get_children():
        tree_employers.delete(row)

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    base_query = """
        SELECT id, company_name, contact_person, phone, email FROM Employer
    """

    # Словарь для сопоставления колонок в интерфейсе с реальными именами в БД
    columns_map = {
        "Название компании": "company_name",
        "Контактное лицо": "contact_person",
        "Телефон": "phone",
        "Email": "email"
    }

    # Если есть поисковый запрос и выбранная колонка
    if search_query and column in columns_map:
        search_query = f"%{search_query}%"
        base_query += f" WHERE {columns_map[column]} LIKE ?"
        cursor.execute(base_query, (search_query,))
    else:
        cursor.execute(base_query)

    # Заполняем таблицу новыми данными
    for row in cursor.fetchall():
        tree_employers.insert("", END, values=row)
    conn.close()



# Удаление нанимателя
def delete_employer():
    selected_item = tree_employers.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите нанимателя для удаления!")
        return

    employer_id = tree_employers.item(selected_item, "values")[0]

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Employer WHERE id=?", (employer_id,))
    conn.commit()
    conn.close()
    refresh_employers()
    messagebox.showinfo("Успех", "Наниматель удален!")

# Изменение нанимателя
def edit_employer():
    selected_item = tree_employers.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите нанимателя для редактирования!")
        return

    employer_id = tree_employers.item(selected_item, "values")[0]

    def save_changes():
        company_name = company_name_var.get()
        contact_person = contact_person_var.get()
        phone = phone_var.get()
        email = email_var.get()

        # Проверка названия компании
        if not company_name:
            messagebox.showerror("Ошибка", "Название компании обязательно!")
            return

        # Проверка телефона
        if not re.fullmatch(r"[+\-0-9]+", phone):
            messagebox.showerror("Ошибка", "Телефон может содержать только цифры, знаки '+' и '-'.")
            return

        # Проверка электронной почты
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Ошибка", "Введите корректный адрес электронной почты!")
            return

        # Сохранение изменений в базу данных
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Employer
            SET company_name = ?, contact_person = ?, phone = ?, email = ?
            WHERE id = ?
        """, (company_name, contact_person, phone, email, employer_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Данные нанимателя обновлены!")
        edit_window.destroy()
        refresh_employers()

    # Получение данных выбранного нанимателя
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, contact_person, phone, email FROM Employer WHERE id=?", (employer_id,))
    employer_data = cursor.fetchone()
    conn.close()

    if not employer_data:
        messagebox.showerror("Ошибка", "Не удалось загрузить данные нанимателя!")
        return

    # Создание окна для редактирования
    edit_window = Toplevel(root)
    edit_window.title("Изменить нанимателя")
    edit_window.geometry("400x300")

    Label(edit_window, text="Название компании").pack(pady=5)
    company_name_var = StringVar(value=employer_data[0])
    Entry(edit_window, textvariable=company_name_var).pack()

    Label(edit_window, text="Контактное лицо").pack(pady=5)
    contact_person_var = StringVar(value=employer_data[1])
    Entry(edit_window, textvariable=contact_person_var).pack()

    Label(edit_window, text="Телефон").pack(pady=5)
    phone_var = StringVar(value=employer_data[2])
    Entry(edit_window, textvariable=phone_var).pack()

    Label(edit_window, text="Email").pack(pady=5)
    email_var = StringVar(value=employer_data[3])
    Entry(edit_window, textvariable=email_var).pack()

    Button(edit_window, text="Сохранить", command=save_changes).pack(pady=10)
    Button(edit_window, text="Отменить", command=edit_window.destroy).pack(pady=5)

def create_report():
    # Открываем файл для записи
    with open("employers_report.txt", "w", encoding="utf-8") as file:
        # Записываем заголовки
        file.write("ID\tНазвание компании\tКонтактное лицо\tТелефон\tEmail\n")

        # Получаем все записи из таблицы и записываем их в файл
        for row in tree_employers.get_children():
            values = tree_employers.item(row, "values")
            file.write("\t".join(str(value) for value in values) + "\n")

    messagebox.showinfo("Отчет", "Отчет успешно создан и сохранен в файл 'employers_report.txt'!")

# Таблица нанимателей
tree_employers = ttk.Treeview(tab_employers, columns=("id", "company_name", "contact_person","phone","email"), show="headings")
tree_employers.heading("id", text="ID")
tree_employers.heading("company_name", text="Название компании")
tree_employers.heading("contact_person", text="Контактное лицо")
tree_employers.heading("phone", text="Номер телефона")
tree_employers.heading("email", text="Email")
tree_employers.pack(expand=1, fill="both")

# Фрейм для элементов поиска нанимателей
search_frame_employers = Frame(tab_employers)
search_frame_employers.pack(fill="x", padx=10, pady=5)

# Метка и поле для ввода текста
Label(search_frame_employers, text="Поиск:").pack(side=LEFT, padx=5)

search_var_employers = StringVar()
Entry(search_frame_employers, textvariable=search_var_employers).pack(side=LEFT, fill="x", expand=True, padx=5)

# Выпадающий список для выбора колонки
Label(search_frame_employers, text="В колонке:").pack(side=LEFT, padx=5)

column_var_employers = StringVar()
column_var_employers.set("Название компании")  # Устанавливаем значение по умолчанию
OptionMenu(search_frame_employers, column_var_employers, "Название компании", "Контактное лицо", "Телефон", "Email").pack(side=LEFT, padx=5)

# Кнопка поиска
search_button_employers = Button(
    search_frame_employers,
    text="Искать",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_employers(search_var_employers.get(), column_var_employers.get())
)
search_button_employers.pack(side=LEFT, padx=5)

# Кнопка сброса фильтра
reset_button_employers = Button(
    search_frame_employers,
    text="Сбросить фильтр",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_employers()
)
reset_button_employers.pack(side=LEFT, padx=5)

# Кнопки для управления нанимателями
frame_employers = Frame(tab_employers)
frame_employers.pack(pady=10)
Button(frame_employers, text="Добавить нанимателя", command=add_employer).pack(side=LEFT, padx=5)
Button(frame_employers, text="Удалить нанимателя", command=delete_employer).pack(side=LEFT, padx=5)
Button(frame_employers, text="Редактировать нанимателя", command=edit_employer).pack(side=LEFT, padx=5)
Button(frame_employers, text="Создать отчет", command=create_report).pack(side=LEFT, padx=5)




# Функции для работы с резюме
def add_resume():
    def save_resume():
        # Получаем значения из выпадающих списков и текстовых полей
        candidate_id = combo_candidate.get()  # ID выбранного кандидата
        vacancy_id = combo_vacancy.get()  # ID выбранной вакансии
        skills = skills_text.get("1.0", "end-1c")
        creation_date = creation_date_var.get()

        if not candidate_id or not vacancy_id or not skills or not creation_date:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            # Проверяем, что ID кандидата и вакансии можно корректно извлечь
            candidate_id = int(candidate_id.split(' - ')[0])  # Извлекаем ID кандидата
            vacancy_id = int(vacancy_id.split(' - ')[0])  # Извлекаем ID вакансии
        except ValueError:
            messagebox.showerror("Ошибка", "ID кандидата и вакансии должны быть числами!")
            return

        try:
            # Проверяем, что дата соответствует формату ГГГГ-ММ-ДД
            datetime.strptime(creation_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        # Сохраняем резюме в базу данных
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Resume (candidate_id, vacancy_id, skills, creation_date) VALUES (?, ?, ?, ?)",
            (candidate_id, vacancy_id, skills, creation_date)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Резюме добавлено!")
        add_window.destroy()
        refresh_resumes()

    # Создаем окно для добавления резюме
    add_window = Toplevel(root)
    add_window.title("Добавить резюме")
    add_window.geometry("400x400")

    # Поле выбора кандидата
    Label(add_window, text="Кандидат").pack(pady=5)
    combo_candidate = ttk.Combobox(add_window, state="readonly")
    combo_candidate.pack()

    # Загрузка данных для выпадающего списка кандидатов
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Candidate")
    candidates = cursor.fetchall()
    combo_candidate["values"] = [f"{c[0]} - {c[1]}" for c in candidates]

    # Поле выбора вакансии
    Label(add_window, text="Вакансия").pack(pady=5)
    combo_vacancy = ttk.Combobox(add_window, state="readonly")
    combo_vacancy.pack()

    # Загрузка данных для выпадающего списка вакансий
    cursor.execute("SELECT id, title FROM Vacancy")
    vacancies = cursor.fetchall()
    combo_vacancy["values"] = [f"{v[0]} - {v[1]}" for v in vacancies]
    conn.close()

    # Поле для ввода навыков
    Label(add_window, text="Навыки").pack(pady=5)
    skills_text = Text(add_window, width=20, height=5, wrap="word")
    skills_text.pack()

    # Поле для ввода даты создания
    Label(add_window, text="Дата создания (ГГГГ-ММ-ДД)").pack(pady=5)
    creation_date_var = StringVar()
    Entry(add_window, textvariable=creation_date_var).pack()

    # Кнопка для сохранения
    Button(add_window, text="Сохранить", command=save_resume).pack(pady=10)

# Обновление списка резюме
def refresh_resumes(search_query=None, column=None):
    # Очищаем таблицу перед загрузкой новых данных
    for row in tree_resumes.get_children():
        tree_resumes.delete(row)

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    # Базовый SQL-запрос
    base_query = """
        SELECT Resume.id, Candidate.name, Vacancy.title, Resume.skills, Resume.creation_date
        FROM Resume
        JOIN Candidate ON Resume.candidate_id = Candidate.id
        JOIN Vacancy ON Resume.vacancy_id = Vacancy.id
    """

    # Словарь для сопоставления колонок в интерфейсе с реальными именами в БД
    columns_map = {
        "Кандидат": "Candidate.name",
        "Вакансия": "Vacancy.title",
        "Навыки": "Resume.skills",
        "Дата создания": "Resume.creation_date"
    }

    # Если есть поисковый запрос, добавляем условие WHERE
    if search_query and column in columns_map:
        search_query = f"%{search_query}%"  # Подготовка шаблона для LIKE
        base_query += f" WHERE {columns_map[column]} LIKE ?"
        cursor.execute(base_query, (search_query,))
    else:
        cursor.execute(base_query)

    # Заполняем таблицу новыми данными
    for row in cursor.fetchall():
        tree_resumes.insert("", "end", values=row)

    conn.close()

# Удаление резюме
def delete_resume():
    selected_item = tree_resumes.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите резюме для удаления!")
        return

    resume_id = tree_resumes.item(selected_item, "values")[0]

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Resume WHERE id=?", (resume_id,))
    conn.commit()
    conn.close()
    refresh_resumes()
    messagebox.showinfo("Успех", "Резюме удалено!")

def edit_resume():
    selected_item = tree_resumes.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите резюме для изменения!")
        return

    # Получаем ID выбранного резюме
    resume_id = tree_resumes.item(selected_item, "values")[0]

    def save_changes():
        # Получаем значения из полей
        new_candidate_id = combo_candidate.get()
        new_vacancy_id = combo_vacancy.get()
        new_skills = skills_text.get("1.0", "end-1c")
        new_creation_date = creation_date_var.get()

        if not new_candidate_id or not new_vacancy_id or not new_skills or not new_creation_date:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            new_candidate_id = int(new_candidate_id.split(' - ')[0])
            new_vacancy_id = int(new_vacancy_id.split(' - ')[0])
        except ValueError:
            messagebox.showerror("Ошибка", "ID кандидата и вакансии должны быть числами!")
            return

        try:
            datetime.strptime(new_creation_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        # Обновляем запись в базе данных
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Resume
            SET candidate_id = ?, vacancy_id = ?, skills = ?, creation_date = ?
            WHERE id = ?
            """,
            (new_candidate_id, new_vacancy_id, new_skills, new_creation_date, resume_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Резюме изменено!")
        edit_window.destroy()
        refresh_resumes()

    # Создаем окно редактирования резюме
    edit_window = Toplevel(root)
    edit_window.title("Изменить резюме")
    edit_window.geometry("400x400")

    # Поле выбора кандидата
    Label(edit_window, text="Кандидат").pack(pady=5)
    combo_candidate = ttk.Combobox(edit_window, state="readonly")
    combo_candidate.pack()

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Candidate")
    candidates = cursor.fetchall()
    combo_candidate["values"] = [f"{c[0]} - {c[1]}" for c in candidates]

    # Поле выбора вакансии
    Label(edit_window, text="Вакансия").pack(pady=5)
    combo_vacancy = ttk.Combobox(edit_window, state="readonly")
    combo_vacancy.pack()

    cursor.execute("SELECT id, title FROM Vacancy")
    vacancies = cursor.fetchall()
    combo_vacancy["values"] = [f"{v[0]} - {v[1]}" for v in vacancies]

    # Поле для ввода навыков
    Label(edit_window, text="Навыки").pack(pady=5)
    skills_text = Text(edit_window, width=20, height=5, wrap="word")
    skills_text.pack()

    # Поле для ввода даты создания
    Label(edit_window, text="Дата создания (ГГГГ-ММ-ДД)").pack(pady=5)
    creation_date_var = StringVar()
    Entry(edit_window, textvariable=creation_date_var).pack()

    # Загрузка текущих данных резюме
    cursor.execute(
        """
        SELECT Candidate.id, Vacancy.id, Resume.skills, Resume.creation_date
        FROM Resume
        JOIN Candidate ON Resume.candidate_id = Candidate.id
        JOIN Vacancy ON Resume.vacancy_id = Vacancy.id
        WHERE Resume.id = ?
        """,
        (resume_id,)
    )
    current_data = cursor.fetchone()
    conn.close()

    if current_data:
        combo_candidate.set(f"{current_data[0]} - {next(c[1] for c in candidates if c[0] == current_data[0])}")
        combo_vacancy.set(f"{current_data[1]} - {next(v[1] for v in vacancies if v[0] == current_data[1])}")
        skills_text.insert("1.0", current_data[2])
        creation_date_var.set(current_data[3])

    # Кнопка для сохранения изменений
    Button(edit_window, text="Сохранить изменения", command=save_changes).pack(pady=10)
    Button(edit_window, text="Отменить", command=edit_window.destroy).pack(pady=5)

def create_report():
    # Открываем файл для записи
    with open("resumes_report.txt", "w", encoding="utf-8") as file:
        # Записываем заголовки
        file.write("ID\tКандидат\tВакансия\tНавыки\tДата создания\n")

        # Получаем все записи из таблицы и записываем их в файл
        for row in tree_resumes.get_children():
            values = tree_resumes.item(row, "values")
            file.write("\t".join(str(value) for value in values) + "\n")

    messagebox.showinfo("Отчет", "Отчет успешно создан и сохранен в файл 'resumes_report.txt'!")

tree_resumes = ttk.Treeview(tab_resumes, columns=("id", "name", "title", "skills", "date"), show="headings")

# Настройка колонок
tree_resumes.heading("id", text="ID")
tree_resumes.column("id", width=50, anchor="center")

tree_resumes.heading("name", text="Кандидат")
tree_resumes.column("name", width=150, anchor="w")

tree_resumes.heading("title", text="Вакансия")
tree_resumes.column("title", width=150, anchor="w")

tree_resumes.heading("skills", text="Навыки")
tree_resumes.column("skills", width=250, anchor="w")

tree_resumes.heading("date", text="Дата создания")
tree_resumes.column("date", width=120, anchor="center")


tree_resumes.pack(fill="both", expand=True, padx=10, pady=10)

# Фрейм для элементов поиска
search_frame = Frame(tab_resumes)
search_frame.pack(fill="x", padx=10, pady=5)

# Метка и поле для ввода текста
Label(search_frame, text="Поиск:").pack(side=LEFT, padx=5)

search_var = StringVar()
Entry(search_frame, textvariable=search_var).pack(side=LEFT, fill="x", expand=True, padx=5)

# Выпадающий список для выбора колонки
Label(search_frame, text="В колонке:").pack(side=LEFT, padx=5)

column_var = StringVar()
column_var.set("Кандидат")  # Устанавливаем значение по умолчанию
OptionMenu(search_frame, column_var, "Кандидат", "Вакансия", "Навыки", "Дата создания").pack(side=LEFT, padx=5)

search_button = Button(
    search_frame,
    text="Искать",
    bg="#4CAF50",  # Зеленый цвет кнопки
    fg="white",    # Белый цвет текста
    font=("Arial", 10, "bold"),
    relief="flat",  # Убираем объем
    command=lambda: refresh_resumes(search_var.get(), column_var.get())
)
search_button.pack(side=LEFT, padx=5)

# Кнопка для сброса фильтра
reset_button = Button(
    search_frame,
    text="Сбросить фильтр",
    bg="#f44336",  # Красный цвет кнопки
    fg="white",    # Белый цвет текста
    font=("Arial", 10, "bold"),
    relief="flat",  # Убираем объем
    command=lambda: refresh_resumes()
)
reset_button.pack(side=LEFT, padx=5)
#Кнопки для управления резюме
frame_resumes = Frame(tab_resumes)
frame_resumes.pack(pady=10)
Button(frame_resumes, text="Добавить резюме", command=add_resume).pack(side=LEFT, padx=5)
Button(frame_resumes, text="Удалить резюме", command=delete_resume).pack(side=LEFT, padx=5)
Button(frame_resumes, text="Изменить резюме", command=edit_resume).pack(side=LEFT, padx=5)
Button(frame_resumes, text="Создать отчет", command=create_report).pack(side=LEFT, padx=5)



# Функции для работы с собеседованиями
from datetime import datetime

def add_interview():
    def save_interview():
        candidate_id = combo_candidate.get().split(" - ")[0]  # Извлекаем только ID
        vacancy_id = combo_vacancy.get().split(" - ")[0]  # Извлекаем только ID
        employer_id = combo_employer.get().split(" - ")[0]  # Извлекаем только ID
        date_time = date_time_var.get()
        result = result_text.get("1.0", "end-1c")

        if not candidate_id or not vacancy_id or not employer_id or not date_time:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            # Проверяем, что дата и время соответствуют формату ГГГГ-ММ-ДД ЧЧ:ММ
            datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата и время должны быть в формате ГГГГ-ММ-ДД ЧЧ:ММ!")
            return

        # Для отладки: выводим данные перед сохранением
        print(
            f"Adding interview: Candidate ID={candidate_id}, Vacancy ID={vacancy_id}, "
            f"Employer ID={employer_id}, DateTime={date_time}, Result={result}")

        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Interview (vacancy_id, candidate_id, employer_id, date_time, result) VALUES (?, ?, ?, ?, ?)",
            (vacancy_id, candidate_id, employer_id, date_time, result),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Собеседование добавлено!")
        add_window.destroy()
        refresh_interviews()

    # Создаем окно для добавления собеседования
    add_window = Toplevel(root)
    add_window.title("Добавить собеседование")
    add_window.geometry("400x400")

    # Поле выбора кандидата
    Label(add_window, text="Кандидат").pack(pady=5)
    combo_candidate = ttk.Combobox(add_window, state="readonly")
    combo_candidate.pack()

    # Поле выбора вакансии
    Label(add_window, text="Вакансия").pack(pady=5)
    combo_vacancy = ttk.Combobox(add_window, state="readonly")
    combo_vacancy.pack()

    # Поле выбора нанимателя
    Label(add_window, text="Наниматель").pack(pady=5)
    combo_employer = ttk.Combobox(add_window, state="readonly")
    combo_employer.pack()

    # Поле для ввода даты и времени
    Label(add_window, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ)").pack(pady=5)
    date_time_var = StringVar()
    Entry(add_window, textvariable=date_time_var).pack()

    # Поле для ввода результата
    Label(add_window, text="Результат").pack(pady=5)
    result_text = Text(add_window, width=20, height=5, wrap="word")
    result_text.pack()

    # Загрузка данных для выпадающих списков
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Candidate")
    candidates = cursor.fetchall()
    combo_candidate["values"] = [f"{c[0]} - {c[1]}" for c in candidates]

    cursor.execute("SELECT id, title FROM Vacancy")
    vacancies = cursor.fetchall()
    combo_vacancy["values"] = [f"{v[0]} - {v[1]}" for v in vacancies]

    cursor.execute("SELECT id, company_name FROM Employer")
    employers = cursor.fetchall()
    combo_employer["values"] = [f"{e[0]} - {e[1]}" for e in employers]

    conn.close()

    # Кнопка для сохранения
    Button(add_window, text="Сохранить", command=save_interview).pack(pady=10)

def refresh_interviews(search_query=None, column=None):
    for row in tree_interviews.get_children():
        tree_interviews.delete(row)

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    base_query = '''
        SELECT 
            Interview.id, 
            Candidate.name, 
            Vacancy.title, 
            Employer.company_name,
            Interview.date_time, 
            Interview.result
        FROM 
            Interview
        JOIN Candidate ON Interview.candidate_id = Candidate.id
        JOIN Vacancy ON Interview.vacancy_id = Vacancy.id
        JOIN Employer ON Interview.employer_id = Employer.id
    '''

    # Словарь для сопоставления колонок в интерфейсе с реальными именами в БД
    columns_map = {
        "Кандидат": "Candidate.name",
        "Вакансия": "Vacancy.title",
        "Наниматель": "Employer.company_name",
        "Дата и время": "Interview.date_time",
        "Результат": "Interview.result"
    }

    # Если есть поисковый запрос и выбранная колонка
    if search_query and column in columns_map:
        search_query = f"%{search_query}%"
        base_query += f" WHERE {columns_map[column]} LIKE ?"
        cursor.execute(base_query, (search_query,))
    else:
        cursor.execute(base_query)

    # Заполняем таблицу новыми данными
    for row in cursor.fetchall():
        tree_interviews.insert("", END, values=row)

    conn.close()

def delete_interview():
    selected_item = tree_interviews.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите собеседование для удаления!")
        return

    interview_id = tree_interviews.item(selected_item, "values")[0]  # Получаем ID собеседования
    confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить собеседование {interview_id}?")
    if confirm:
        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Interview WHERE id = ?", (interview_id,))
        conn.commit()
        conn.close()
        refresh_interviews()  # Обновляем таблицу после удаления
        messagebox.showinfo("Успех", "Собеседование удалено!")

def edit_interview():
    selected_item = tree_interviews.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите собеседование для редактирования!")
        return

    # Получаем данные выбранного собеседования
    interview_id = tree_interviews.item(selected_item, "values")[0]

    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT vacancy_id, candidate_id, employer_id, date_time, result
        FROM Interview
        WHERE id = ?
    ''', (interview_id,))
    interview_data = cursor.fetchone()
    conn.close()

    if not interview_data:
        messagebox.showerror("Ошибка", "Собеседование не найдено!")
        return

    def save_changes():
        vacancy_id = combo_vacancy.get().split(" - ")[0]
        candidate_id = combo_candidate.get().split(" - ")[0]
        employer_id = combo_employer.get().split(" - ")[0]
        date_time = date_time_var.get()
        result = result_text.get("1.0", "end-1c")

        if not candidate_id or not vacancy_id or not employer_id or not date_time:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        try:
            # Проверяем, что дата и время соответствуют формату ГГГГ-ММ-ДД ЧЧ:ММ
            datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата и время должны быть в формате ГГГГ-ММ-ДД ЧЧ:ММ!")
            return

        conn = sqlite3.connect("recruiting_agency.db")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Interview
            SET vacancy_id = ?, candidate_id = ?, employer_id = ?, date_time = ?, result = ?
            WHERE id = ?
        ''', (vacancy_id, candidate_id, employer_id, date_time, result, interview_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Собеседование обновлено!")
        edit_window.destroy()
        refresh_interviews()

    # Создаем окно для редактирования собеседования
    edit_window = Toplevel(root)
    edit_window.title("Редактировать собеседование")
    edit_window.geometry("400x400")

    # Поле выбора кандидата
    Label(edit_window, text="Кандидат").pack(pady=5)
    combo_candidate = ttk.Combobox(edit_window, state="readonly")
    combo_candidate.pack()

    # Поле выбора вакансии
    Label(edit_window, text="Вакансия").pack(pady=5)
    combo_vacancy = ttk.Combobox(edit_window, state="readonly")
    combo_vacancy.pack()

    # Поле выбора нанимателя
    Label(edit_window, text="Наниматель").pack(pady=5)
    combo_employer = ttk.Combobox(edit_window, state="readonly")
    combo_employer.pack()

    # Поле для ввода даты и времени
    Label(edit_window, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ)").pack(pady=5)
    date_time_var = StringVar(value=interview_data[3])
    Entry(edit_window, textvariable=date_time_var).pack()

    # Поле для ввода результата
    Label(edit_window, text="Результат").pack(pady=5)
    result_text = Text(edit_window, width=20, height=5, wrap="word")
    result_text.insert("1.0", interview_data[4])
    result_text.pack()

    # Загрузка данных для выпадающих списков
    conn = sqlite3.connect("recruiting_agency.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Candidate")
    candidates = cursor.fetchall()
    combo_candidate["values"] = [f"{c[0]} - {c[1]}" for c in candidates]
    combo_candidate.set(f"{interview_data[1]} - {next(c[1] for c in candidates if c[0] == interview_data[1])}")

    cursor.execute("SELECT id, title FROM Vacancy")
    vacancies = cursor.fetchall()
    combo_vacancy["values"] = [f"{v[0]} - {v[1]}" for v in vacancies]
    combo_vacancy.set(f"{interview_data[0]} - {next(v[1] for v in vacancies if v[0] == interview_data[0])}")

    cursor.execute("SELECT id, company_name FROM Employer")
    employers = cursor.fetchall()
    combo_employer["values"] = [f"{e[0]} - {e[1]}" for e in employers]
    combo_employer.set(f"{interview_data[2]} - {next(e[1] for e in employers if e[0] == interview_data[2])}")

    conn.close()

    # Кнопка для сохранения
    Button(edit_window, text="Сохранить изменения", command=save_changes).pack(pady=10)
    Button(edit_window, text="Отменить", command=edit_window.destroy).pack(pady=5)


def create_report():
    # Открываем файл для записи
    with open("interview_report.txt", "w", encoding="utf-8") as file:
        # Записываем заголовки
        file.write("ID\tКандидат\tВакансия\tНаниматель\tДата и Время\tРезультат\n")

        # Получаем все записи из таблицы и записываем их в файл
        for row in tree_interviews.get_children():
            values = tree_interviews.item(row, "values")
            file.write("\t".join(str(value) for value in values) + "\n")

    messagebox.showinfo("Отчет", "Отчет успешно создан и сохранен в файл 'interview_report.txt'!")

# Таблица собеседований
tree_interviews = ttk.Treeview(tab_interviews, columns=("id", "candidate", "vacancy", "employer", "date_time", "result"), show="headings")
tree_interviews.heading("id", text="ID")
tree_interviews.heading("candidate", text="Кандидат")
tree_interviews.heading("vacancy", text="Вакансия")
tree_interviews.heading("employer", text="Наниматель")
tree_interviews.heading("date_time", text="Дата и время")
tree_interviews.heading("result", text="Результат")
tree_interviews.pack(expand=1, fill="both")

# Фрейм для элементов поиска собеседований
search_frame_interviews = Frame(tab_interviews)
search_frame_interviews.pack(fill="x", padx=10, pady=5)

# Метка и поле для ввода текста
Label(search_frame_interviews, text="Поиск:").pack(side=LEFT, padx=5)

search_var_interviews = StringVar()
Entry(search_frame_interviews, textvariable=search_var_interviews).pack(side=LEFT, fill="x", expand=True, padx=5)

# Выпадающий список для выбора колонки
Label(search_frame_interviews, text="В колонке:").pack(side=LEFT, padx=5)

column_var_interviews = StringVar()
column_var_interviews.set("Кандидат")  # Устанавливаем значение по умолчанию
OptionMenu(search_frame_interviews, column_var_interviews, "Кандидат", "Вакансия", "Наниматель", "Дата и время", "Результат").pack(side=LEFT, padx=5)

# Кнопка поиска
search_button_interviews = Button(
    search_frame_interviews,
    text="Искать",
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_interviews(search_var_interviews.get(), column_var_interviews.get())
)
search_button_interviews.pack(side=LEFT, padx=5)

# Кнопка сброса фильтра
reset_button_interviews = Button(
    search_frame_interviews,
    text="Сбросить фильтр",
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    command=lambda: refresh_interviews()
)
reset_button_interviews.pack(side=LEFT, padx=5)


# Кнопки для управления собеседованиями
frame_interviews = Frame(tab_interviews)
frame_interviews.pack(pady=10)
Button(frame_interviews, text="Добавить собеседование", command=add_interview).pack(side=LEFT, padx=5)
Button(frame_interviews, text="Удалить собеседование", command=delete_interview).pack(side=LEFT, padx=5)
Button(frame_interviews, text="Изменить собеседование", command=edit_interview).pack(side=LEFT, padx=5)
Button(frame_interviews, text="Создать отчет", command=create_report).pack(side=LEFT, padx=5)

# Инициализация базы данных и загрузка данных
init_db()
refresh_candidates()

# Загрузка данных вакансий
refresh_vacancies()

# Загрузка данных нанимателей
refresh_employers()

# Обновление данных резюме при запуске
refresh_resumes()

# Обновление данных резюме при запуске
refresh_interviews()

# Запуск приложения
root.mainloop()
