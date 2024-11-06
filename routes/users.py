from fastapi import APIRouter, Depends

from models.models import Users, User
from database import async_session, get_db
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

users_router = APIRouter(prefix="/users", tags=["Пользователи"])



@users_router.post("/testAdd/", response_model=User)
async def create_user(username: str, hashed_password: str, balance: int,  db: AsyncSession = Depends(get_db)):
    new_user = Users(username=username, hashed_password=hashed_password, balance=balance)
    new_user.id = uuid.uuid4()
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user