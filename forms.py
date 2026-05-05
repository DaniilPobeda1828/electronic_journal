from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Email, Optional
from datetime import datetime

# ==================== ФОРМА АВТОРИЗАЦИИ ====================
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[
        DataRequired(message='Введите логин'),
        Length(min=3, max=50, message='Логин должен быть от 3 до 50 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    submit = SubmitField('Войти')

# ==================== ФОРМЫ ДЛЯ АДМИНИСТРАТОРА ====================
class GroupForm(FlaskForm):
    name = StringField('Название группы', validators=[
        DataRequired(message='Введите название группы'),
        Length(min=2, max=20, message='Название должно быть от 2 до 20 символов')
    ])
    submit = SubmitField('Добавить группу')

class StudentForm(FlaskForm):
    full_name = StringField('ФИО студента', validators=[
        DataRequired(message='Введите ФИО'),
        Length(min=5, max=100, message='ФИО должно быть от 5 до 100 символов')
    ])
    birth_date = DateField('Дата рождения', validators=[
        DataRequired(message='Выберите дату рождения')
    ], format='%Y-%m-%d')
    group_id = SelectField('Группа', coerce=int, validators=[
        DataRequired(message='Выберите группу')
    ])
    submit = SubmitField('Добавить студента')
    
    def validate_birth_date(self, field):
        if field.data > datetime.now().date():
            raise ValidationError('Дата рождения не может быть в будущем')
        if field.data.year < 1950:
            raise ValidationError('Некорректная дата рождения')

class SubjectForm(FlaskForm):
    name = StringField('Название предмета', validators=[
        DataRequired(message='Введите название предмета'),
        Length(min=2, max=100, message='Название должно быть от 2 до 100 символов')
    ])
    teacher_id = SelectField('Преподаватель', coerce=int, validators=[
        DataRequired(message='Выберите преподавателя')
    ])
    submit = SubmitField('Добавить предмет')

class UserForm(FlaskForm):
    login = StringField('Логин', validators=[
        DataRequired(message='Введите логин'),
        Length(min=3, max=50, message='Логин должен быть от 3 до 50 символов')
    ])
    full_name = StringField('ФИО', validators=[
        DataRequired(message='Введите ФИО'),
        Length(min=5, max=100, message='ФИО должно быть от 5 до 100 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=4, max=50, message='Пароль должен быть от 4 до 50 символов')
    ])
    role = SelectField('Роль', choices=[
        ('admin', 'Администратор'),
        ('teacher', 'Преподаватель'),
        ('student', 'Студент')
    ], validators=[DataRequired()])
    submit = SubmitField('Добавить пользователя')

# ==================== ФОРМЫ ДЛЯ ПРЕПОДАВАТЕЛЯ ====================
class GradeForm(FlaskForm):
    student_id = SelectField('Студент', coerce=int, validators=[
        DataRequired(message='Выберите студента')
    ])
    subject_id = HiddenField('ID предмета')
    grade = SelectField('Оценка', choices=[
        (2, '2 (неудовлетворительно)'),
        (3, '3 (удовлетворительно)'),
        (4, '4 (хорошо)'),
        (5, '5 (отлично)')
    ], coerce=int, validators=[DataRequired()])
    work_type = SelectField('Тип работы', choices=[
        ('лекция', 'Лекция'),
        ('практика', 'Практика'),
        ('экзамен', 'Экзамен')
    ], validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()], 
                     default=datetime.now, format='%Y-%m-%d')
    submit = SubmitField('Выставить оценку')
    
    def validate_date(self, field):
        if field.data > datetime.now().date():
            raise ValidationError('Дата не может быть в будущем')

# ==================== ФОРМЫ ДЛЯ ОТЧЁТОВ ====================
class GroupSelectForm(FlaskForm):
    group_id = SelectField('Выберите группу', coerce=int, validators=[
        DataRequired(message='Выберите группу')
    ])
    submit = SubmitField('Показать')

class ExportForm(FlaskForm):
    group_id = SelectField('Группа для экспорта', coerce=int, validators=[
        DataRequired(message='Выберите группу')
    ])
    submit = SubmitField('Экспортировать в Excel')