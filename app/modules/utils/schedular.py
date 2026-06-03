from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database.dependencies import SessionLocal
from app.modules.seats.model import MovieSeat
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def release_expired_seats():
    db: Session = SessionLocal()

    try:
        now = datetime.utcnow()

        db.query(MovieSeat).filter(
            MovieSeat.status == "HELD",
            MovieSeat.held_until < now
        ).update({
            MovieSeat.status: "AVAILABLE",
            MovieSeat.held_until: None
        }, synchronize_session=False)

        db.commit()

    except Exception as e:
        db.rollback()
        print("Expiry error:", e)

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(release_expired_seats, "interval", seconds=60)
    scheduler.start()
