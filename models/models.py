from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, UUID4
from typing import List, Optional
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

    id_user = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, nullable=False, unique=True, index=True)
    balance = Column(Numeric(10, 2), default=0)

    tokens = relationship("JwtTokens", back_populates="user", cascade="all, delete-orphan")

class JwtTokens(Base):
    __tablename__ = "jwt_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id_user"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    revoked = Column(Boolean, default=False)

    user = relationship("Users", back_populates="tokens")
class User(BaseModel):
    id_user: UUID4
    username: str
    balance: float

class UserCreate(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class GraphemeRequest(BaseModel):
    graphemes: List[str]

class GraphemeResponse(BaseModel):
    available_graphemes: List[str]

class ConfirmResponse(BaseModel):
    confirm: bool

class TokenDetail(BaseModel):
    token: str
    pinyin: str
    meanings: List[str]

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    tokens: List[TokenDetail]