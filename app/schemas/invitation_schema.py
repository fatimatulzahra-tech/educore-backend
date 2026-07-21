from pydantic import BaseModel


class InvitePrincipalRequest(
    BaseModel
):

    email: str

    school_id: int


class AcceptInvitationRequest(
    BaseModel
):

    token: str

    password: str