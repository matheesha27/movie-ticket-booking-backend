from sqlalchemy import Column, BigInteger, String, Integer

from app.database.session import Base

class Cinema(Base):

    __tablename__ = "cinemas"

    id = Column(BigInteger, primary_key=True, index=True)

    name = Column(String, nullable=False)
    city = Column(String)
    total_capacity = Column(Integer)
