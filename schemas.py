from pydantic import BaseModel


class LawyerCreate(BaseModel):
    email: str
    password: str


class LeadBase(BaseModel):
    name: str
    email: str
    accident_type: str
    injury_description: str
    liability: str


class LeadCreate(LeadBase):
    pass


class LeadOut(LeadBase):
    id: int
    score: int | None = None
    case_strength: str | None = None
    summary: str | None = None

    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    accident_type: str | None = None
    injury_description: str | None = None
    liability: str | None = None
    status: str | None = None

