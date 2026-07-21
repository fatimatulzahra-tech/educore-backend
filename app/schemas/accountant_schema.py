from pydantic import BaseModel, EmailStr


class AccountantCreate(BaseModel):

    first_name: str

    last_name: str

    email: EmailStr

    phone: str