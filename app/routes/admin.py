from fastapi import APIRouter, UploadFile, File, HTTPException
from app.db import Database
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/admin")


# Utility function to save uploaded files
async def save_file(file: UploadFile):
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        buffer.write(await file.read())
    return str(file_location)


# Add Service
@router.post("/add-service/")
async def add_service(name: str, description: str, image: UploadFile = File(...)):
    conn = Database.pool
    try:
        image_path = await save_file(image)
        await conn.execute(
            """
            INSERT INTO services (image_path, name, description)
            VALUES ($1, $2, $3)
            """,
            image_path, name, description
        )
        return {"message": "Service added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Get All Services
@router.get("/get-all-services/")
async def get_all_services():
    conn = Database.pool
    try:
        services = await conn.fetch("SELECT * FROM services")
        if not services:
            raise HTTPException(status_code=404, detail="No services found.")
        return {"services": [dict(service) for service in services]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Add Team Member
@router.post("/add-team-member/")
async def add_team_member(name: str, designation: str, description: str, image: UploadFile = File(...)):
    conn = Database.pool
    try:
        image_path = await save_file(image)
        await conn.execute(
            """
            INSERT INTO team_members (image_path, name, designation, description)
            VALUES ($1, $2, $3, $4)
            """,
            image_path, name, designation, description
        )
        return {"message": "Team member added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Get All Team Members
@router.get("/get-all-team-members/")
async def get_all_team_members():
    conn = Database.pool
    try:
        team_members = await conn.fetch("SELECT * FROM team_members")
        if not team_members:
            raise HTTPException(status_code=404, detail="No team members found.")
        return {"team_members": [dict(member) for member in team_members]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Add Event
@router.post("/add-event/")
async def add_event(name: str, description: str, price: float, image: UploadFile = File(...)):
    conn = Database.pool
    try:
        image_path = await save_file(image)
        await conn.execute(
            """
            INSERT INTO events (pic_path, name, description, price)
            VALUES ($1, $2, $3, $4)
            """,
            image_path, name, description, price
        )
        return {"message": "Event added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Get All Events
@router.get("/get-all-events/")
async def get_all_events():
    conn = Database.pool
    try:
        events = await conn.fetch("SELECT * FROM events")
        if not events:
            raise HTTPException(status_code=404, detail="No events found.")
        return {
            "events": [
                {
                    "id": event["id"],
                    "name": event["name"],
                    "description": event["description"],
                    "price": event["price"],
                    "pic_path": event["pic_path"]
                }
                for event in events
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Admin Get All Table Bookings
@router.get("/get-all-bookings/")
async def get_all_bookings():
    conn = Database.pool
    try:
        bookings = await conn.fetch("SELECT * FROM bookings")
        if not bookings:
            raise HTTPException(status_code=404, detail="No table bookings found.")
        return {
            "bookings": [dict(booking) for booking in bookings]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Delete a Team Member
@router.delete("/delete-team-member/{id}/")
async def delete_team_member(id: int):
    conn = Database.pool
    try:
        result = await conn.execute("DELETE FROM team_members WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows were deleted
            raise HTTPException(status_code=404, detail=f"Team member with ID {id} not found.")
        return {"message": "Team member deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Delete a Service
@router.delete("/delete-service/{id}/")
async def delete_service(id: int):
    conn = Database.pool
    try:
        result = await conn.execute("DELETE FROM services WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows were deleted
            raise HTTPException(status_code=404, detail=f"Service with ID {id} not found.")
        return {"message": "Service deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Delete an Event
@router.delete("/delete-event/{id}/")
async def delete_event(id: int):
    conn = Database.pool
    try:
        result = await conn.execute("DELETE FROM events WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows were deleted
            raise HTTPException(status_code=404, detail=f"Event with ID {id} not found.")
        return {"message": "Event deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
# Delete a Booking by ID
@router.delete("/delete-booking/{id}/")
async def delete_booking(id: int):
    conn = Database.pool
    try:
        result = await conn.execute("DELETE FROM bookings WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows were deleted
            raise HTTPException(status_code=404, detail=f"Booking with ID {id} not found.")
        return {"message": "Booking deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
