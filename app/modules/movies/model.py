from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime, func, Integer
from sqlalchemy.ext.hybrid import hybrid_property

from app.database.session import Base

class Movie(Base):

    __tablename__ = "movies"

    id = Column(BigInteger, primary_key=True, index=True)
    cinema_id = Column(BigInteger, ForeignKey("cinemas.id"))

    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String)
    duration = Column(Integer)
    banner_image = Column(String)
    trailer = Column(String)
    show_time = Column(DateTime, default=func.now())
    status = Column(String, default="ACTIVE")

    @hybrid_property
    def formatted_time(self):
        return self.created_at.strftime('%I:%M %p') if self.created_at else None
