from fastapi import FastAPI
from app.startup import startup, shutdown
from app.routes import user, booking, contact_us, admin

app = FastAPI()

# Register startup and shutdown events
app.on_event("startup")(startup)
app.on_event("shutdown")(shutdown)

# Add routes to the app
app.include_router(user.router, prefix="/users")
app.include_router(booking.router, prefix="/bookings")
app.include_router(contact_us.router, prefix="/contact-us")
app.include_router(admin.router, prefix="/admin")

@app.get("/")
def root():
    return {"message": "Welcome to the Modular Hotel Backend API!"}