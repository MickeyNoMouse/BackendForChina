from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, UUID4
from typing import List
import uuid

Base = declarative_base()

class Hieroglyphs(Base):
    __tablename__ = "hieroglyphs"
    unicode = Column(String, primary_key=True, index=True)

    hieroglyph_parts = relationship("Hieroglyph_Parts", back_populates="hieroglyph")


class Parts_hieroglyphs(Base):
    __tablename__ = "parts_hieroglyphs"
    id_part_hieroglyph = Column(Integer, primary_key=True, index=True)
    part = Column(String, index=True)

    hieroglyph_parts = relationship("Hieroglyph_Parts", back_populates="part")


class Hieroglyph_Parts(Base):
    __tablename__ = "hieroglyph_parts"
    id_hieroglyph = Column(String, ForeignKey("hieroglyphs.unicode"), primary_key=True)
    id_part_hieroglyph = Column(Integer, ForeignKey("parts_hieroglyphs.id_part_hieroglyph"), primary_key=True)

    hieroglyph = relationship("Hieroglyphs", back_populates="hieroglyph_parts")
    part = relationship("Parts_hieroglyphs", back_populates="hieroglyph_parts")


class Users(Base):
    __tablename__ = "users"

    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Integer, default=0)

class User(BaseModel):
    id_user: UUID4
    username: str
    balance: int

class GraphemeRequest(BaseModel):
    graphemes: List[str]

class GraphemeResponse(BaseModel):
    available_graphemes: List[str]

class ConfirmResponse(BaseModel):
    confirm: bool
