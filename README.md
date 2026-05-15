# 📚 **ТЕХНИЧЕСКАЯ ДОКУМЕНТАЦИЯ**
## Электронный журнал успеваемости студентов


[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://github.com/antistereotip/Badges-for-GitHub?ysclid=mp5efi9xb7512975989)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

---

## 📋 **СОДЕРЖАНИЕ**

1. [Введение](#1-введение)
2. [Архитектура системы](#2-архитектура-системы)
3. [Установка и запуск](#3-установка-и-запуск)
4. [Модели данных](#4-модели-данных)
5. [API маршруты](#5-api-маршруты)
6. [Роли и права доступа](#6-роли-и-права-доступа)
7. [Интерфейс пользователя](#7-интерфейс-пользователя)
8. [Тестирование](#8-тестирование)
9. [Заключение](#9-заключение)

---

## 1. ВВЕДЕНИЕ

### 1.1. Назначение системы

Электронный журнал успеваемости студентов предназначен для автоматизации учёта учебного процесса в учебных заведениях. Система обеспечивает:

- Ведение базы данных студентов, групп, преподавателей и предметов
- Выставление и хранение оценок с указанием типа работы и даты
- Автоматический расчёт среднего балла
- Формирование отчётов (должники, отличники, сравнение групп)
- Экспорт данных в Excel
- Ведение расписания занятий
- Разграничение прав доступа (администратор, преподаватель, студент)
- Логирование всех действий пользователей

### 1.2. Технический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык программирования** | Python | 3.13+ |
| **Веб-фреймворк** | Flask | 2.3.3 |
| **База данных** | SQLite | 3 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Авторизация** | Flask-Login | 0.6.2 |
| **Формы** | Flask-WTF | 1.1.1 |
| **Фронтенд** | Bootstrap 5 | 5.1.3 |
| **Графики** | Chart.js | 4.4+ |
| **Экспорт Excel** | pandas + openpyxl | 2.0.3 |
| **Тестирование** | pytest | 9.0+ |

### 1.3. Системные требования

| Параметр | Минимальное значение | Рекомендуемое |
|----------|---------------------|---------------|
| ОЗУ | 256 МБ | 512 МБ |
| Процессор | 1 ГГц | 2 ГГц |
| Дисковое пространство | 100 МБ | 500 МБ |
| Операционная система | Windows 7 / Linux / macOS | Windows 10+ |

---

## 2. АРХИТЕКТУРА СИСТЕМЫ

### 2.1. Общая архитектура

```
┌──────────────────────────────────────────────────────────────────┐
│                         Клиент (Браузер)                         │
│                    HTML / CSS / JavaScript / Bootstrap           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Flask Application (app.py)                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ │
│ │    Routes   │ │   Models    │ │    Forms    │ │     Auth     │ │
│ │  (Маршруты) │ │ (Модели БД) │ │   (Формы)   │ │ (Декораторы) │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                        SQLite Database                           │
│              (users, groups, students, subjects,                 │
│               grades, schedule, action_logs, messages)           │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2. Структура проекта

```
electronic_journal/
│
├── app.py                     # Главный файл приложения
├── config.py                  # Конфигурация
├── auth.py                    # Декораторы ролей
├── forms.py                   # WTForms
├── models.py                  # Файл с формами
├── requirements.txt           # Зависимости
├── instance/                  # папка создается автоматически при запуске проекта
│   └── journal.db             # База данных
├── static/
│   ├── css/
│   │   └── style.css          # Стили
│   └── js/
│       └── charts.js          # Графики
├── templates/
│   ├── base.html              # Базовый шаблон
│   ├── login.html             # Страница входа
│   ├── index.html             # Главная страница
│   ├── admin/                 # Шаблоны админа
│   ├── teacher/               # Шаблоны преподавателя
│   ├── student/               # Шаблоны студента
│   ├── reports/               # Шаблоны отчётов
│   ├── schedule/              # Шаблоны расписания
│   └── messages/              # Шаблоны сообщений
├── tests/                     # Тесты
│   ├── conftest.py
│   ├── test_admin.py
│   ├── test_auth.py
│   ├── test_models.py
│   ├── test_reports.py
│   ├── test_schedule.py
│   ├── test_student.py
│   └── test_teacher.py

```

---

## 3. УСТАНОВКА И ЗАПУСК

### 3.1. Установка зависимостей

```bash
# Клонирование репозитория
git clone https://github.com/your-repo/electronic_journal.git
cd electronic_journal

# Установка зависимостей
pip install -r requirements.txt
```

### 3.2. Содержимое `requirements.txt`

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
openpyxl==3.1.2
pandas==2.0.3
bcrypt==4.0.1
pytest==9.0.2
pytest-cov==7.0.0
```

### 3.3. Настройка конфигурации (config.py)

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///journal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    
    EXCELLENT_THRESHOLD = 4.75
    DEBTOR_THRESHOLD = 3.0
```

### 3.4. Запуск приложения

```bash
# Режим разработки
python app.py

# Режим продакшена (через Gunicorn)
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

### 3.5. Первый запуск

При первом запуске автоматически создаются:
- База данных `journal.db`
- Тестовый администратор: **admin / admin123**

```
==================================================
Тестовый администратор создан:
Логин: admin
Пароль: admin123
==================================================
 * Running on http://127.0.0.1:5000
```

---

## 4. МОДЕЛИ ДАННЫХ

### 4.1. Диаграмма базы данных

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │     │   Student   │     │    Group    │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │◄─── │ user_id (FK)│     │ id (PK)     │
│ login       │     │ id (PK)     │     │ name        │
│ password    │     │ full_name   │────►│ group_id(FK)│
│ role        │     │ birth_date  │     └─────────────┘
│ full_name   │     │ group_id(FK)│
└─────────────┘     └─────────────┘
       │                   │
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│   Subject   │     │    Grade    │
├─────────────┤     ├─────────────┤
│ id (PK)     │     │ id (PK)     │
│ name        │     │ student_id  │
│ teacher_id  │◄─── │ subject_id  │
└─────────────┘     │ grade       │
                    │ date        │
                    │ work_type   │
                    └─────────────┘
```

### 4.2. Описание моделей

#### **User** — пользователи системы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `login` | String(50) | Уникальный логин |
| `password_hash` | String(200) | Хэш пароля |
| `role` | String(20) | Роль (admin/teacher/student) |
| `full_name` | String(100) | Полное имя |
| `created_at` | DateTime | Дата создания |

#### **Group** — учебные группы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `name` | String(20) | Название группы |
| `created_at` | DateTime | Дата создания |

#### **Student** — студенты

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `full_name` | String(100) | ФИО |
| `birth_date` | Date | Дата рождения |
| `group_id` | Integer | FK → Group |
| `user_id` | Integer | FK → User |

#### **Subject** — учебные предметы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `name` | String(100) | Название предмета |
| `teacher_id` | Integer | FK → User |
| `created_at` | DateTime | Дата создания |

#### **Grade** — оценки

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `student_id` | Integer | FK → Student |
| `subject_id` | Integer | FK → Subject |
| `grade` | Integer | Оценка (2-5) |
| `date` | Date | Дата выставления |
| `work_type` | String(20) | Тип работы |

#### **Schedule** — расписание

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `group_id` | Integer | FK → Group |
| `subject_id` | Integer | FK → Subject |
| `classroom` | String(20) | Номер кабинета |
| `day_of_week` | Integer | День недели (1-7) |
| `start_time` | String(5) | Время начала |
| `end_time` | String(5) | Время окончания |

#### **ActionLog** — логи действий

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `user_id` | Integer | FK → User |
| `action` | String(200) | Действие |
| `target` | String(200) | Объект действия |
| `ip_address` | String(50) | IP-адрес |
| `timestamp` | DateTime | Время действия |

#### **Message** — сообщения

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer | Первичный ключ |
| `from_user_id` | Integer | FK → User (отправитель) |
| `to_user_id` | Integer | FK → User (получатель) |
| `subject` | String(200) | Тема |
| `content` | Text | Содержание |
| `is_read` | Boolean | Прочитано |
| `created_at` | DateTime | Дата отправки |

---

## 5. API МАРШРУТЫ

### 5.1. Авторизация

| Метод | Маршрут | Описание | Доступ |
|-------|---------|----------|--------|
| GET | `/login` | Страница входа | Все |
| POST | `/login` | Обработка входа | Все |
| GET | `/logout` | Выход из системы | Авторизованные |

### 5.2. Администратор

| Метод | Маршрут | Описание |
|-------|---------|----------|
| GET | `/admin` | Панель администратора |
| GET | `/admin/groups` | Управление группами |
| POST | `/admin/groups/add` | Добавление группы |
| POST | `/admin/groups/edit/<id>` | Редактирование группы |
| GET | `/admin/groups/delete/<id>` | Удаление группы |
| GET | `/admin/students` | Управление студентами |
| POST | `/admin/students/add` | Добавление студента |
| POST | `/admin/students/edit/<id>` | Редактирование студента |
| GET | `/admin/students/delete/<id>` | Удаление студента |
| GET | `/admin/subjects` | Управление предметами |
| POST | `/admin/subjects/add` | Добавление предмета |
| GET | `/admin/logs` | Просмотр логов |
| GET | `/admin/schedule` | Управление расписанием |
| POST | `/admin/schedule/add` | Добавление занятия |
| GET | `/admin/schedule/delete/<id>` | Удаление занятия |

### 5.3. Преподаватель

| Метод | Маршрут | Описание |
|-------|---------|----------|
| GET | `/teacher` | Панель преподавателя |
| GET | `/teacher/grades/<subject_id>` | Выставление оценок |
| POST | `/teacher/add_grade` | Добавление оценки |
| GET | `/teacher/group_grades/<group_id>` | Успеваемость группы |

### 5.4. Студент

| Метод | Маршрут | Описание |
|-------|---------|----------|
| GET | `/student/my_grades` | Мои оценки |

### 5.5. Отчёты

| Метод | Маршрут | Описание |
|-------|---------|----------|
| GET | `/reports/debtors` | Список должников |
| GET | `/reports/excellent` | Список отличников |
| GET | `/reports/compare_groups` | Сравнение групп |
| GET | `/reports/charts` | Графики успеваемости |
| GET | `/export/group/<group_id>` | Экспорт в Excel |

### 5.6. Расписание и сообщения

| Метод | Маршрут | Описание |
|-------|---------|----------|
| GET | `/schedule` | Просмотр расписания |
| GET | `/messages/send` | Отправка сообщения |
| POST | `/messages/send` | Отправка сообщения |
| GET | `/messages/inbox` | Входящие сообщения |
| GET | `/messages/read/<id>` | Чтение сообщения |
| GET | `/messages/delete/<id>` | Удаление сообщения |

---

## 6. РОЛИ И ПРАВА ДОСТУПА

### 6.1. Матрица доступа

| Функция | Администратор | Преподаватель | Студент |
|---------|:-------------:|:-------------:|:-------:|
| Вход в систему | ✅ | ✅ | ✅ |
| Просмотр своих оценок | ✅ | ✅ | ✅ |
| Выставление оценок | ✅ | ✅ | ❌ |
| Управление группами | ✅ | ❌ | ❌ |
| Управление студентами | ✅ | ❌ | ❌ |
| Управление предметами | ✅ | ❌ | ❌ |
| Управление пользователями | ✅ | ❌ | ❌ |
| Просмотр логов | ✅ | ❌ | ❌ |
| Просмотр расписания | ✅ | ✅ | ✅ |
| Редактирование расписания | ✅ | ❌ | ❌ |
| Отчёты | ✅ | ✅ | ❌ |
| Экспорт Excel | ✅ | ✅ | ❌ |
| Сообщения | ✅ | ✅ | ❌ |

### 6.2. Декораторы ролей

```python
# Только для администратора
@admin_required
def admin_only_route():
    pass

# Для преподавателя или администратора
@teacher_required
def teacher_or_admin_route():
    pass

# Для студента
@student_required
def student_only_route():
    pass
```

---

## 7. ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ

### 7.1. Структура страниц

```
Электронный журнал
│
├── Страница входа (/login)
│   └── Форма авторизации
│
├── Главная страница (/)
│   ├── Приветствие
│   ├── Статистика (админ)
│   ├── Список предметов (преподаватель)
│   └── Кнопка "Мои оценки" (студент)
│
├── Администратор
│   ├── Управление группами (/admin/groups)
│   ├── Управление студентами (/admin/students)
│   ├── Управление предметами (/admin/subjects)
│   ├── Управление пользователями (/admin/users)
│   ├── Журнал действий (/admin/logs)
│   └── Управление расписанием (/admin/schedule)
│
├── Преподаватель
│   ├── Мои предметы (/teacher)
│   ├── Выставление оценок (/teacher/grades/<id>)
│   └── Успеваемость группы (/teacher/group_grades/<id>)
│
├── Студент
│   └── Мои оценки (/student/my_grades)
│
└── Отчёты
    ├── Должники (/reports/debtors)
    ├── Отличники (/reports/excellent)
    ├── Сравнение групп (/reports/compare_groups)
    └── Графики (/reports/charts)
```

### 7.2. Основные компоненты UI

#### **Базовый шаблон (base.html)**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Электронный журнал{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <!-- Навигационная панель -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        ...
    </nav>
    
    <!-- Основной контент -->
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <!-- Подвал -->
    <footer class="footer">
        ...
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 8. ТЕСТИРОВАНИЕ

### 8.1. Запуск тестов

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с отчётом о покрытии
pytest tests/ --cov=. --cov-report=html

# Запуск конкретного тестового файла
pytest tests/test_auth.py -v
```

### 8.2. Результаты тестирования

```
====================================================================================================
platform win32 -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0
collected 27 items

tests/test_admin.py ...                                                               [ 11%]
tests/test_auth.py ....                                                               [ 25%]
tests/test_models.py ....                                                             [ 40%]
tests/test_reports.py .....                                                           [ 59%]
tests/test_schedule.py ..                                                             [ 66%]
tests/test_student.py .....                                                           [ 85%]
tests/test_teacher.py ....                                                            [100%]

================================= 27 passed, 5 warnings in 12.01s ==================================
```

### 8.3. Структура тестов

```python
# Пример теста авторизации
class TestAuth:
    def test_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_valid_admin_login(self, client):
        response = client.post('/login', data={
            'login': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
```

---

## 9. ЗАКЛЮЧЕНИЕ

### 9.1. Выполненные требования

| Требование ТЗ | Статус |
|---------------|--------|
| Управление группами и студентами | ✅ |
| Управление предметами и оценками | ✅ |
| Автоматический подсчёт среднего балла | ✅ |
| Отчёты (должники, отличники, сравнение групп) | ✅ |
| Журнал действий (логи) | ✅ |
| Роли и права доступа | ✅ |
| Авторизация с хэшированием | ✅ |
| Экспорт в Excel | ✅ |
| График успеваемости | ✅ |
| Расписание занятий | ✅ |
| Система сообщений | ✅ |

### 9.2. Характеристики ПО

| Параметр | Значение | Способ замера |
|----------|----------|---------------|
| Время запуска | 2.3 сек | Секундомер |
| Открытие журнала группы | 0.5 сек | Секундомер |
| Расчёт среднего балла | 0.1 сек | Секундомер |
| Потребление ОЗУ | 45 МБ | Диспетчер задач |

### 9.3. Контактная информация

**Разработчик:** [Манусевич Даниил Вадимович]  
**GitHub** [https://github.com/DaniilPobeda1828/electronic_journal]


---

**© 2026 | Электронный журнал успеваемости студентов**

*Все права защищены*
