from pydantic import BaseModel


class AdminResetPasswordRequest(BaseModel):

    user_id: int