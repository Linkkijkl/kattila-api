from pydantic import BaseModel, Field


class SeurantaUser(BaseModel):
    username: str = Field(pattern="[a-zA-Z0-9]{2,30}")
    memberships: list[str] | None = None
    board_memberships: list[str] | None = None


class SeurantaUsers(BaseModel):
    users: list[SeurantaUser] = []
