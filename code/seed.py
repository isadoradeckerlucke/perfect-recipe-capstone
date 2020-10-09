from models import User, db
from app import app 

db.drop_all()
db.create_all()

User.query.delete()

db.session.commit()