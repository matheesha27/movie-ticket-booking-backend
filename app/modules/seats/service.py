from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.modules.seats.model import MovieSeat, SeatHold


def generate_unique_seat_id(
    cinema_id: int,
    movie_id: int,
    date,
    show_time: str,
    seat_name: str
):

    if isinstance(date, datetime):
        date = date.strftime("%Y%m%d")

    return (
        f"{cinema_id}/"
        f"{movie_id}/"
        f"{date}/"
        f"{show_time}/"
        f"{seat_name}"
    )


# def cleanup_expired_holds():
#
#     db = SessionLocal()
#
#     try:
#
#         now = datetime.utcnow()
#
#         expired_ids = (
#             db.query(SeatHold.unique_movie_seat_id)
#             .filter(
#                 SeatHold.expires_at < now
#             )
#             .subquery()
#         )
#
#         (
#             db.query(MovieSeat)
#             .filter(
#                 MovieSeat.unique_movie_seat.in_(expired_ids)
#             )
#             .filter(
#                 MovieSeat.status == "HELD"
#             )
#             .update(
#                 {
#                     "status": "AVAILABLE",
#                     "held_at": None,
#                     "held_until": None
#                 },
#                 synchronize_session=False
#             )
#         )
#
#         (
#             db.query(SeatHold)
#             .filter(
#                 SeatHold.expires_at < now
#             )
#             .delete(
#                 synchronize_session=False
#             )
#         )
#
#         db.commit()
#
#     except Exception:
#         db.rollback()
#         raise
#
#     finally:
#         db.close()
