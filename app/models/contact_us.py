from pydantic import BaseModel, EmailStr

class ContactUsInput(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str