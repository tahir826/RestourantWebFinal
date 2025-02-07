from fastapi import APIRouter, HTTPException
from app.models.booking import BookingInput
from app.db import Database

router = APIRouter()

# Ensure the 'id' and 'phone_no' columns exist in the database
async def ensure_table_structure():
    conn = await Database.pool.acquire()
    try:
        # Ensure 'id' column exists (auto-incrementing SERIAL column)
        id_column_check_query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'bookings' AND column_name = 'id';
        """
        id_column_exists = await conn.fetchval(id_column_check_query)
        if not id_column_exists:
            await conn.execute("ALTER TABLE bookings ADD COLUMN id SERIAL PRIMARY KEY;")
            print("Added 'id' column with SERIAL to the bookings table.")

        # Ensure 'phone_no' column exists
        phone_no_column_check_query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'bookings' AND column_name = 'phone_no';
        """
        phone_no_column_exists = await conn.fetchval(phone_no_column_check_query)
        if not phone_no_column_exists:
            await conn.execute("ALTER TABLE bookings ADD COLUMN phone_no VARCHAR(20);")
            print("Added 'phone_no' column to the bookings table.")
    except Exception as e:
        print(f"Error ensuring table structure: {e}")
    finally:
        await Database.pool.release(conn)


@router.post("/book-table/")
async def book_table(booking: BookingInput):
    # Ensure table structure before inserting data
    await ensure_table_structure()

    conn = await Database.pool.acquire()
    try:
        # Insert query: No need to specify the 'id', it will be auto-incremented
        result = await conn.fetchrow(
            """
            INSERT INTO bookings (user_id, name, email, phone_no, datetime, no_of_people, special_request)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id;
            """,
            booking.user_id, booking.name, booking.email, booking.phone_no,
            booking.datetime, booking.no_of_people, booking.special_request
        )
        generated_id = result["id"]  # Automatically returned from the database
        return {"message": "Table booked successfully.", "booking_id": generated_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await Database.pool.release(conn)


@router.get("/get-bookings/{user_id}")
async def get_bookings(user_id: str):
    # Ensure the database structure is valid
    await ensure_table_structure()

    conn = Database.pool
    bookings = await conn.fetch("SELECT * FROM bookings WHERE user_id = $1", user_id)
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user.")

    return {
        "user_id": user_id,
        "bookings": [
            {
                "id": booking["id"],  # Include the auto-incremented id
                "name": booking["name"],
                "email": booking["email"],
                "phone_no": booking["phone_no"],  # Include phone_no
                "datetime": booking["datetime"],
                "no_of_people": booking["no_of_people"],
                "special_request": booking["special_request"]
            } for booking in bookings
        ]
    }