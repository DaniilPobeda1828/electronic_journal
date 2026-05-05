import os

class Config:
    # Секретный ключ для сессий (в продакшене заменить на реальный)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # Путь к базе данных
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "journal.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Роли пользователей
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    
    # Типы работ
    WORK_TYPES = ['лекция', 'практика', 'экзамен']
    
    # Допустимые оценки
    GRADES = [2, 3, 4, 5]
    
    # Пороги для отчётности
    EXCELLENT_THRESHOLD = 4.75  # Отличники (средний балл >= 4.75)
    DEBTOR_THRESHOLD = 3.0      # Должники (средний балл < 3.0)
    
    # Папки
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    EXPORTS_FOLDER = os.path.join(BASE_DIR, 'exports')
    
    # Создание папок, если их нет
    @staticmethod
    def init_folders():
        folders = [Config.LOGS_FOLDER, Config.EXPORTS_FOLDER]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)