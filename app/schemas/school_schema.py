from pydantic import BaseModel, EmailStr


class SchoolCreate(BaseModel):

    name: str
    slug: str
    email: EmailStr
    phone: str
    address: str

class InviteUser(BaseModel):

    email: EmailStr
    role: str

class AcceptInvitationRequest(BaseModel):

    token: str
    password: str