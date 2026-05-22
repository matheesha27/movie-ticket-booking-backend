from fastapi import FastAPI
from modules.users.routes import router as user_router

app = FastAPI()
app.include_router(user_router, prefix="/users")

@app.get("/")
def root():
    return {"message": "Ticket Booking API Running"}


