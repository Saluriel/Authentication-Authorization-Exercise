from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()

u1 = User(
    username="username",
    password="password",
    email='email',
    first_name='firstname',
    last_name='lastname'
)

u2 = User(
    username="greg",
    password="password",
    email='gregsemail',
    first_name='greg',
    last_name='gregson'
)


db.session.add(u1)
db.session.add(u2)
db.session.commit()

f1 = Feedback(
    title = 'testfeedback',
    content='testing the feedback here it is!!!!!!',
    username='username'
)

f2 = Feedback(
    title = 'testfeedback2',
    content='222222testing the feedback here it is!!!!!!',
    username='username'
)

f3 = Feedback(
    title = 'testfeedback',
    content='testing the feedback here it is!!!!!!',
    username='greg'
)

db.session.add(f1)
db.session.add(f2)
db.session.add(f3)
db.session.commit()