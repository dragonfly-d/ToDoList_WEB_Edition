from data.users import User
from data.tasks import Tasks
from data import db_session

db_session.global_init('db/TDLDataBase.db')

db_sess = db_session.create_session()
user_name = db_sess.query(User.name).filter(User.id == 4).first()
print(str(user_name)[2:-3])
