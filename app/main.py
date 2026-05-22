from fastapi import FastAPI
from app.modules.users.routes import router as user_router
from app.modules.auth.routes import router as auth_router

app = FastAPI()
app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "Ticket Booking API Running"}
