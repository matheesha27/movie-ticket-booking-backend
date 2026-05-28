from fastapi_mail import FastMail, MessageSchema
from app.config.email_config import conf

async def send_otp_email(email: str, otp: str):

    message = MessageSchema(
        subject = "Cinemax - Your booking OTP",
        recipients = [email],
        body = f"""
Your OTP for booking verification: {otp}.
This expires in 5 minutes.""",
        subtype = "plain"
    )

    fm = FastMail(conf)

    await fm.send_message(message)
