from fastapi import APIRouter
from app.models.contact_us import ContactUsInput
from app.db import Database

router = APIRouter()

@router.post("/")
async def contact_us(contact: ContactUsInput):
    conn = Database.pool
    await conn.execute(
        """
        INSERT INTO contact_us (name, email, subject, message)
        VALUES ($1, $2, $3, $4)
        """,
        contact.name, contact.email, contact.subject, contact.message
    )
    return {"message": "Thank you for reaching out to us. We will get back to you soon!"}