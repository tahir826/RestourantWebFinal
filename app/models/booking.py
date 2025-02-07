from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timezone

class BookingInput(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    phone_no: str
    datetime: datetime
    no_of_people: int
    special_request: str = None

    @validator("datetime", pre=True, always=True)
    def ensure_timezone(cls, value):
        # Convert string to datetime if necessary
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        
        # Ensure the datetime is timezone-aware
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
