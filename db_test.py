from data.users import User
from data.tasks import Tasks
from data import db_session

db_session.global_init('db/TDLDataBase.db')

# Ниже показан пример создания новой записи в таблицу users
user = User()
user.name = "Пользователь 1"
user.email = "email1@email.ru"
# Обязательно пароль через метод set_password, дабы хешировать пароль
user.set_password('123456789')
db_sess = db_session.create_session()
db_sess.add(user)
db_sess.commit()

# Ниже показан пример создания новой записи в таблицу tasks
task = Tasks()
task.title = 'Написать код для бд'
task.done = 1  # default = 0
task.user_id = user.id # Берем id юзера
db_sess.add(task)
db_sess.commit()
