from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime

from app.database.session import Base

class Movie(Base):

    __tablename__ = "movies"

    id = Column(BigInteger, primary_key=True, index=True)
    cinema_id = Column(BigInteger,ForeignKey("cinemas.id"))

    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    banner_image = Column(String)
    show_time = Column(DateTime)
    status = Column(String, default="ACTIVE")
