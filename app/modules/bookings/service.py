from fastapi_mail import FastMail, MessageSchema
from app.config.email_config import conf

async def send_otp_email(email: str, otp: str):

    message = MessageSchema(
        subject="Cinemax - Your booking OTP",
        recipients=[email],
        body=f"""
Your OTP for booking verification: {otp}.
This OTP expires in 5 minutes.""",
        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(message)

async def send_confirmation_email(payload: dict, booking_reference: str):

    message = MessageSchema(
        subject="CineMax - Booking Confirmation - Ref. #" + booking_reference,
        recipients=[payload.get("email")],
        body=f"""
Booking Confirmed

Movie: {payload.get("movie_title")}
Cinema: {payload.get("cinema_name")}
Seats: {payload.get("seats")}
Amount Paid: LKR {payload.get("total_price")}

Unique Movie Seat:
{payload.get("unique_movie_seat_id")}

Booking Reference:
{booking_reference}
""",
        subtype="plain"
    )

    fm = FastMail(conf)

    await fm.send_message(message)
