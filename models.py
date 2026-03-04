from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    leads = relationship("Lead", back_populates="lawyer")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    accident_type = Column(String)
    injury_description = Column(String)
    liability = Column(String)

    score = Column(Integer)
    case_strength = Column(String)
    summary = Column(String)
    status = Column(String, default="New")

    lawyer_id = Column(Integer, ForeignKey("lawyers.id"))
    lawyer = relationship("Lawyer", back_populates="leads")
