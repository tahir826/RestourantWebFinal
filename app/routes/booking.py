from fastapi import APIRouter, HTTPException
from app.models.booking import BookingInput
from app.db import Database

router = APIRouter()

@router.post("/book-table/")
async def book_table(booking: BookingInput):
    conn = await Database.pool.acquire()
    try:
        await conn.execute(
            """
            INSERT INTO bookings (user_id, name, email, datetime, no_of_people, special_request)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            booking.user_id, booking.name, booking.email, booking.datetime, booking.no_of_people, booking.special_request
        )
        return {"message": "Table booked successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await Database.pool.release(conn)

@router.get("/get-bookings/{user_id}")
async def get_bookings(user_id: str):
    conn = Database.pool
    bookings = await conn.fetch("SELECT * FROM bookings WHERE user_id = $1", user_id)
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user.")

    return {
        "user_id": user_id,
        "bookings": [
            {
                "name": booking["name"],
                "email": booking["email"],
                "datetime": booking["datetime"],
                "no_of_people": booking["no_of_people"],
                "special_request": booking["special_request"]
            } for booking in bookings
        ]
    }