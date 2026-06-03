from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import User

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    users = db.query(User).all()

    return users