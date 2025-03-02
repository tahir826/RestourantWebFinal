from fastapi import FastAPI
from app.startup import startup, shutdown
from app.routes import user, booking, contact_us, admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Register startup and shutdown events
app.on_event("startup")(startup)
app.on_event("shutdown")(shutdown)
# Define allowed origins (your frontend URL)
origins = [
    "https://yummy-yatch.netlify.app",  # Your frontend
    "http://localhost:3000",  # Optional: Allow local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from frontend
    allow_credentials=True,  # Allow cookies/auth
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
@app.get("/")
def root():
    return {"message": "Welcome to the Modular Hotel Backend API!"}

# Add routes to the app
app.include_router(user.router, prefix="/users")
app.include_router(booking.router, prefix="/bookings")
app.include_router(contact_us.router, prefix="/contact-us")
app.include_router(admin.router, prefix="/admin")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)