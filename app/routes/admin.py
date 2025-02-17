from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from app.db import Database
from app.config import UPLOAD_DIR
from pydantic import BaseModel, EmailStr, validator
import json
from pathlib import Path



router = APIRouter(prefix="/admin")
class SubPackage(BaseModel):
    name: str
    price: float


class Package(BaseModel):
    name: str
    price: float
    subpackages: List[SubPackage]


class MenuDisplayInput(BaseModel):
    occasion_id: int
    packages: List[Package]

# Utility function to save uploaded files
async def save_files(files: List[UploadFile]):
    file_paths = []
    for file in files:
        file_location = UPLOAD_DIR / file.filename
        with file_location.open("wb") as buffer:
            buffer.write(await file.read())
        file_paths.append(str(file_location))
    return file_paths


@router.on_event("startup")
async def create_occasions_table():
    conn = Database.pool
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS occasions (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                heading TEXT NOT NULL,
                description TEXT NOT NULL,
                price FLOAT NOT NULL,
                tags JSONB NOT NULL,
                images JSONB NOT NULL
            )
        """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating occasions table: {str(e)}")
async def save_file(file: UploadFile) -> str:
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        buffer.write(await file.read())
    return str(file_location)
@router.get("/get-all-occasions/")
async def get_all_occasions():
    """
    Fetches all occasions from the database.

    Returns:
        List of occasions with their details.
    """
    conn = Database.pool
    try:
        occasions = await conn.fetch("SELECT * FROM occasions")
        if not occasions:
            raise HTTPException(status_code=404, detail="No occasions found.")
        return {
            "occasions": [
                {
                    "id": occasion["id"],
                    "name": occasion["name"],
                    "heading": occasion["heading"],
                    "description": occasion["description"],
                    "price": occasion["price"],
                    "standard_price": occasion["standard_price"],  # New field
                    "outstandard_price": occasion["outstandard_price"],
                    "tags": occasion["tags"],
                    "images": occasion["images"]
                }
                for occasion in occasions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching occasions: {str(e)}")


# Get Occasion By ID
@router.get("/get-occasion/{id}/")
async def get_occasion_by_id(id: int):
    """
    Fetches a specific occasion by its ID.

    Args:
        id (int): The ID of the occasion.

    Returns:
        Occasion details if found.
    """
    conn = Database.pool
    try:
        occasion = await conn.fetchrow("SELECT * FROM occasions WHERE id = $1", id)
        if not occasion:
            raise HTTPException(status_code=404, detail=f"Occasion with ID {id} not found.")
        return {
            "id": occasion["id"],
            "name": occasion["name"],
            "heading": occasion["heading"],
            "description": occasion["description"],
            "price": occasion["price"],
            "standard_price": occasion["standard_price"],  # New field
            "outstandard_price": occasion["outstandard_price"],
            "tags": occasion["tags"],
            "images": occasion["images"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching occasion: {str(e)}")


# Delete Occasion By ID
@router.delete("/delete-occasion/{id}/")
async def delete_occasion_by_id(id: int):
    """
    Deletes an occasion by its ID.

    Args:
        id (int): The ID of the occasion to delete.

    Returns:
        Success message if deleted.
    """
    conn = Database.pool
    try:
        result = await conn.execute("DELETE FROM occasions WHERE id = $1", id)
        if result == "DELETE 0":  # If no rows were deleted
            raise HTTPException(status_code=404, detail=f"Occasion with ID {id} not found.")
        return {"message": "Occasion deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting occasion: {str(e)}")

# Add Occasion Route
@router.post("/add-occasion/")
async def add_occasion(
    name: str,
    heading: str,
    description: str,
    price: float,
    standard_price: float,  # New field
    outstandard_price: float,  # New field
    tags: List[str],
    images: List[UploadFile] = File(...)
):
    """
    Adds a new occasion to the database.

    Args:
        name (str): The name of the occasion.
        heading (str): A heading for the occasion.
        description (str): A description of the occasion.
        price (float): The price of the occasion.
        standard_price (float): The standard price of the occasion.
        outstandard_price (float): The outstandard price of the occasion.
        tags (List[str]): A list of tags for the occasion.
        images (List[UploadFile]): A list of image files for the occasion.

    Returns:
        dict: A success message.
    """
    conn = Database.pool
    try:
        # Save the uploaded images
        image_paths = await save_files(images)

        # Insert the occasion into the database
        await conn.execute(
            """
            INSERT INTO occasions (name, heading, description, price, standard_price, outstandard_price, tags, images)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            name,
            heading,
            description,
            price,
            standard_price,  # Add the standard price
            outstandard_price,  # Add the outstandard price
            json.dumps(tags),  # Convert tags list to JSON
            json.dumps(image_paths)  # Convert image paths list to JSON
        )

        return {"message": "Occasion added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding occasion: {str(e)}")

@router.post("/add-menu/")
async def add_menu(
    heading: str = Form(...),
    heading_image: UploadFile = File(...),
    dish_names: List[str] = Form(...),
    dish_images: List[UploadFile] = File(...)
):
    """
    Add a new menu with a heading, heading image, and a list of dishes (each with a name and image).
    """
    conn = Database.pool

    try:
        # Save the heading image
        heading_image_path = await save_file(heading_image)

        # Insert heading into the database
        heading_id = await conn.fetchval(
            """
            INSERT INTO menu_headings (heading, heading_image)
            VALUES ($1, $2)
            RETURNING id
            """,
            heading,
            heading_image_path
        )

        for dish_name, dish_image in zip(dish_names, dish_images):
            dish_image_path = await save_file(dish_image)
            await conn.execute(
                """
                INSERT INTO dishes (menu_id, name, image)
                VALUES ($1, $2, $3)
                """,
                heading_id,
                dish_name,
                dish_image_path
            )

        return {"message": "Menu added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding menu: {str(e)}")


@router.get("/get-all-menu/")
async def get_all_menu():
    """
    Get all menus with their headings, images, and associated dishes.
    """
    conn = Database.pool

    try:
        # Fetch all headings
        headings = await conn.fetch("SELECT * FROM menu_headings")

        if not headings:
            raise HTTPException(status_code=404, detail="No menus found.")

        # Fetch associated dishes for each heading
        all_menus = []
        for heading in headings:
            dishes = await conn.fetch(
                """
                SELECT * FROM dishes WHERE menu_id = $1
                """,
                heading["id"]
            )
            all_menus.append({
                "id": heading["id"],
                "heading": heading["heading"],
                "heading_image": heading["heading_image"],
                "dishes": [
                    {
                        "id": dish["id"],
                        "name": dish["name"],
                        "image": dish["image"]
                    } for dish in dishes
                ]
            })

        return {"menus": all_menus}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menus: {str(e)}")


@router.get("/get-menu-by-heading-id/{heading_id}/")
async def get_menu_by_heading_id(heading_id: int):
    """
    Get a specific menu by its heading ID, including the heading image and associated dishes.
    """
    conn = Database.pool

    try:
        # Fetch the heading
        heading = await conn.fetchrow(
            """
            SELECT * FROM menu_headings WHERE id = $1
            """,
            heading_id
        )

        if not heading:
            raise HTTPException(status_code=404, detail="Menu heading not found.")

        # Fetch associated dishes
        dishes = await conn.fetch(
            """
            SELECT * FROM dishes WHERE menu_id = $1
            """,
            heading_id
        )

        return {
            "id": heading["id"],
            "heading": heading["heading"],
            "heading_image": heading["heading_image"],
            "dishes": [
                {
                    "id": dish["id"],
                    "name": dish["name"],
                    "image": dish["image"]
                } for dish in dishes
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menu: {str(e)}")

@router.delete("/delete-menu/{heading_id}/")
async def delete_menu(heading_id: int):
    """
    Delete a menu by its heading ID, including all associated dishes.

    Args:
        heading_id (int): The ID of the menu heading to delete.

    Returns:
        dict: Success message if the menu is deleted successfully.
    """
    conn = Database.pool

    try:
        # Check if the heading exists
        heading = await conn.fetchrow(
            """
            SELECT * FROM menu_headings WHERE id = $1
            """,
            heading_id
        )

        if not heading:
            raise HTTPException(status_code=404, detail="Menu heading not found.")

        # Delete the associated dishes
        await conn.execute(
            """
            DELETE FROM dishes WHERE menu_id = $1
            """,
            heading_id
        )

        # Delete the menu heading
        await conn.execute(
            """
            DELETE FROM menu_headings WHERE id = $1
            """,
            heading_id
        )

        return {"message": f"Menu with heading ID {heading_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting menu: {str(e)}")



@router.post("/add-menu-display/")
async def add_menu_display(menu: MenuDisplayInput):
    conn = Database.pool

    # Check if the occasion ID exists
    occasion_exists = await conn.fetchval(
        "SELECT COUNT(*) FROM occasions WHERE id = $1", menu.occasion_id
    )

    if not occasion_exists:
        raise HTTPException(status_code=400, detail="Invalid occasion ID.")

    try:
        # Insert packages into the database
        for package in menu.packages:
            package_id = await conn.fetchval(
                """
                INSERT INTO packages (occasion_id, name, price)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                menu.occasion_id,
                package.name,
                package.price
            )

            # Insert subpackages for each package
            for subpackage in package.subpackages:
                await conn.execute(
                    """
                    INSERT INTO subpackages (package_id, name, price)
                    VALUES ($1, $2, $3)
                    """,
                    package_id,
                    subpackage.name,
                    subpackage.price
                )

        return {"message": "Menu display added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding menu display: {str(e)}")


@router.get("/get-menu-display/{occasion_id}/")
async def get_menu_display(occasion_id: int):
    """
    Retrieves the menu display for a specific occasion.

    Args:
        occasion_id (int): The ID of the occasion.

    Returns:
        dict: The menu display including packages and subpackages.
    """
    conn = app.state.db_pool

    try:
        # Fetch packages for the occasion
        packages = await conn.fetch(
            """
            SELECT * FROM packages WHERE occasion_id = $1
            """,
            occasion_id
        )

        if not packages:
            raise HTTPException(status_code=404, detail="No packages found for this occasion.")

        # Fetch subpackages for each package
        menu_display = []
        for package in packages:
            subpackages = await conn.fetch(
                """
                SELECT * FROM subpackages WHERE package_id = $1
                """,
                package["id"]
            )

            menu_display.append({
                "package_id": package["id"],
                "name": package["name"],
                "price": package["price"],
                "subpackages": [
                    {
                        "subpackage_id": subpackage["id"],
                        "name": subpackage["name"],
                        "price": subpackage["price"]
                    } for subpackage in subpackages
                ]
            })

        return {"occasion_id": occasion_id, "menu_display": menu_display}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menu display: {str(e)}")


@router.get("/get-subpackages/{package_id}/")
async def get_subpackages(package_id: int):
    """
    Retrieves subpackages for a specific package.

    Args:
        package_id (int): The ID of the package.

    Returns:
        dict: The subpackages for the package.
    """
    conn = app.state.db_pool

    try:
        subpackages = await conn.fetch(
            """
            SELECT * FROM subpackages WHERE package_id = $1
            """,
            package_id
        )

        if not subpackages:
            raise HTTPException(status_code=404, detail="No subpackages found for this package.")

        return {
            "package_id": package_id,
            "subpackages": [
                {
                    "subpackage_id": subpackage["id"],
                    "name": subpackage["name"],
                    "price": subpackage["price"]
                } for subpackage in subpackages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subpackages: {str(e)}")


@router.delete("/delete-menu-display/{occasion_id}/")
async def delete_menu_display(occasion_id: int):
    """
    Deletes a menu display for a specific occasion, including all associated packages and subpackages.

    Args:
        occasion_id (int): The ID of the occasion whose menu display should be deleted.

    Returns:
        dict: A success message if the deletion is successful.
    """
    # Acquire a connection from the pool
    async with app.state.db_pool.acquire() as conn:
        try:
            # Check if the occasion exists
            occasion_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM occasions WHERE id = $1", occasion_id
            )

            if not occasion_exists:
                raise HTTPException(status_code=404, detail="Occasion not found.")

            # Start a transaction
            async with conn.transaction():
                # Delete subpackages associated with the packages of the occasion
                await conn.execute(
                    """
                    DELETE FROM subpackages
                    WHERE package_id IN (
                        SELECT id FROM packages WHERE occasion_id = $1
                    )
                    """,
                    occasion_id
                )

                # Delete packages associated with the occasion
                await conn.execute(
                    """
                    DELETE FROM packages WHERE occasion_id = $1
                    """,
                    occasion_id
                )

                # Delete the occasion itself
                await conn.execute(
                    """
                    DELETE FROM occasions WHERE id = $1
                    """,
                    occasion_id
                )

            return {"message": f"Menu display for occasion ID {occasion_id} deleted successfully."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting menu display: {str(e)}")
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