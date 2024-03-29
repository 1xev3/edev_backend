from pydantic import BaseModel, Field

class SectionCreate(BaseModel):
    name: str = Field(title="Section name")

class SectionUpdate(SectionCreate):
    pass

class Section(SectionCreate):
    id: int = Field(title="Section ID")

