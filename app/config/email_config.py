import os
from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_FROM_NAME="CineMax - Movie Ticket Booking",

    # 💡 CRITICAL BREVO AND PORT 2525 ROUTING CONFIGURATION:
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_PORT=2525,  # Bypasses the Render port 587 block completely
    MAIL_STARTTLS=True,  # Must be True for port 2525
    MAIL_SSL_TLS=False,  # Must be False for port 2525

    USE_CREDENTIALS=True
    # VALIDATE_CERTS=True
)