from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.bookings.service import send_otp_email

router = APIRouter()

@router.get("/test/db")
def test(db: Session = Depends(get_db)):
    return {"ok": True}

@router.get("/test-email")
async def test_email():

    await send_otp_email(
        "matheesha27@gmail.com",
        "123456"
    )

    return {"status": "sent"}