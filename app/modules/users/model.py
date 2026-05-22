from sqlalchemy import Column, BigInteger, String
from app.database.session import Base

class User(Base):

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)