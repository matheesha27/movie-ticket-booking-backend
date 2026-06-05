import os
from fastapi_mail import ConnectionConfig
from app.config.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_FROM_NAME="CineMax - Movie Ticket Booking",

    # 💡 CRITICAL BREVO AND PORT 2525 ROUTING CONFIGURATION:
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_PORT=587,  # Bypasses the Render port 587 block completely
    MAIL_STARTTLS=True,  # Must be True for port 2525
    MAIL_SSL_TLS=False,  # Must be False for port 2525

    USE_CREDENTIALS=True
    # VALIDATE_CERTS=True
)

print(os.getenv("MAIL_USERNAME"))
print(os.getenv("MAIL_PASSWORD"));
print(os.getenv("MAIL_FROM"));
