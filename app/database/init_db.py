from app.database.session import engine, Base
from app.modules.users.model import User

Base.metadata.create_all(bind=engine)