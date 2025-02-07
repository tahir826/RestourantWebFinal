from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.db import Database
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/admin")


# Utility function to save uploaded files
async def save_file(file: UploadFile):
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        buffer.write(await file.read())
    return str(file_location)


@router.get("/get-all-contacts/")
async def get_all_contacts():
    conn = Database.pool
    try:
        # Fetch all contact messages from the contact_us table
        contacts = await conn.fetch("SELECT * FROM contact_us")
        if not contacts:  # If no contacts found
            raise HTTPException(status_code=404, detail="No contact messages found.")
        
        # Return the list of contact messages
        return {
            "contacts": [dict(contact) for contact in contacts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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

# Delete a Contact Us Message by ID
@router.delete("/delete-contact/{id}/")
async def delete_contact(id: int):
    conn = Database.pool
    try:
        # Execute DELETE query on the contact_us table
        result = await conn.execute("DELETE FROM contact_us WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows are deleted
            raise HTTPException(status_code=404, detail=f"Contact message with ID {id} not found.")
        return {"message": "Contact message deleted successfully."}
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
@router.put("/update-event/{id}/")
async def update_event(id: int, name: str = None, description: str = None, price: float = None, image: UploadFile = None):
    conn = Database.pool
    try:
        update_columns = []
        values = []

        if name:
            update_columns.append("name = $1")
            values.append(name)
        if description:
            update_columns.append("description = $" + str(len(values) + 1))
            values.append(description)
        if price is not None:
            update_columns.append("price = $" + str(len(values) + 1))
            values.append(price)
        if image:
            image_path = await save_file(image)
            update_columns.append("pic_path = $" + str(len(values) + 1))
            values.append(image_path)
        
        if not update_columns:
            raise HTTPException(status_code=400, detail="No fields to update were provided.")

        values.append(id)
        update_query = f"""
            UPDATE events 
            SET {', '.join(update_columns)} 
            WHERE id = ${len(values)}
        """
        result = await conn.execute(update_query, *values)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail=f"Event with ID {id} not found.")
        return {"message": "Event updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# Update Service
@router.put("/update-service/{id}/")
async def update_service(id: int, name: str = None, description: str = None, image: UploadFile = None):
    conn = Database.pool
    try:
        update_columns = []
        values = []

        if name:
            update_columns.append("name = $1")
            values.append(name)
        if description:
            update_columns.append("description = $" + str(len(values) + 1))
            values.append(description)
        if image:
            image_path = await save_file(image)
            update_columns.append("image_path = $" + str(len(values) + 1))
            values.append(image_path)
        
        if not update_columns:
            raise HTTPException(status_code=400, detail="No fields to update were provided.")

        values.append(id)
        update_query = f"""
            UPDATE services 
            SET {', '.join(update_columns)} 
            WHERE id = ${len(values)}
        """
        result = await conn.execute(update_query, *values)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail=f"Service with ID {id} not found.")
        return {"message": "Service updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Update Team Member
@router.put("/update-team-member/{id}/")
async def update_team_member(id: int, name: str = None, designation: str = None, description: str = None, image: UploadFile = None):
    conn = Database.pool
    try:
        update_columns = []
        values = []

        if name:
            update_columns.append("name = $1")
            values.append(name)
        if designation:
            update_columns.append("designation = $" + str(len(values) + 1))
            values.append(designation)
        if description:
            update_columns.append("description = $" + str(len(values) + 1))
            values.append(description)
        if image:
            image_path = await save_file(image)
            update_columns.append("image_path = $" + str(len(values) + 1))
            values.append(image_path)
        
        if not update_columns:
            raise HTTPException(status_code=400, detail="No fields to update were provided.")

        values.append(id)
        update_query = f"""
            UPDATE team_members 
            SET {', '.join(update_columns)} 
            WHERE id = ${len(values)}
        """
        result = await conn.execute(update_query, *values)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail=f"Team member with ID {id} not found.")
        return {"message": "Team member updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")