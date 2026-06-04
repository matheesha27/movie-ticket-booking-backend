import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database.dependencies import SessionLocal
from app.modules.seats.model import MovieSeat, SeatHold
from datetime import datetime
from sqlalchemy import func, cast, DateTime

scheduler = BackgroundScheduler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def release_expired_seats():
    db: Session = SessionLocal()

    try:
        now = datetime.utcnow()

        # Release HELD seats after expiry
        held_seat_rows = db.query(MovieSeat).filter(
            MovieSeat.status == "HELD",
            MovieSeat.held_until < now
        ).update({
            MovieSeat.status: "AVAILABLE",
            MovieSeat.held_until: None
        }, synchronize_session=False)

        # Delete row from seat_holds table
        db.query(SeatHold).filter(
            SeatHold.expires_at < now
        ).delete(synchronize_session=False)

        # Build the sqlAlchemy db type datetime string
        db_datetime_str = func.concat(
            func.split_part(MovieSeat.unique_movie_seat, '/', 3),
            ' ',
            func.split_part(MovieSeat.unique_movie_seat, '/', 4)
        )

        # Change status to EXPIRE for past date/time movie_seats
        past_movie_rows = db.query(MovieSeat).filter(
            MovieSeat.status != "EXPIRED",
            cast(func.to_timestamp(db_datetime_str, 'YYYYMMDD HH24MI'), DateTime) <= now
        ).update(
            {MovieSeat.status: "EXPIRED"},
            synchronize_session=False
        )

        db.commit()
        if held_seat_rows > 0:
            logger.info(f"Successfully released {held_seat_rows} expired HELD movie seats.")
        elif held_seat_rows == 0:
            logger.info(f"All HELD seats are already released.")
        if past_movie_rows > 0:
            logger.info(f"Successfully expired {past_movie_rows} past movie seats.")
        elif past_movie_rows == 0:
            logger.info(f"All past movie seats are already flagged EXPIRED.")

    except Exception as e:
        db.rollback()
        print("Expiry error:", e)

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(release_expired_seats, "interval", seconds=60)
    scheduler.start()
