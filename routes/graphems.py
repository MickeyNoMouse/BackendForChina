from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.models import Parts_hieroglyphs
from sqlalchemy import  select

graphems_router = APIRouter(prefix="/graphems", tags=["Графемы"])

#получение списка всех графем
@graphems_router.get("/all_graphems", response_model=list)
async def get_all_graphems(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Parts_hieroglyphs.part))
        result = result.scalars()
        if not result:
            raise HTTPException(status_code=404, detail="No graphems found")

    return result