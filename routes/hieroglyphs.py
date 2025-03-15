from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from models.models import (Hieroglyphs, Hieroglyph_Parts, Parts_hieroglyphs,
                           GraphemeRequest, GraphemeResponse, ConfirmResponse, HieroglyphResponse)
from database import get_db
from itertools import groupby
from collections import Counter

hieroglyphs_router = APIRouter(prefix="/hieroglyphs", tags=["Иероглифы"])


@hieroglyphs_router.get("/random_hieroglyph", response_model=str)
async def get_random_hieroglyph(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Hieroglyphs.unicode).order_by(func.random()).limit(1))
        hieroglyph_unicode = result.scalar()

        if not hieroglyph_unicode:
            raise HTTPException(status_code=404, detail="No hieroglyphs found")

    return hieroglyph_unicode


@hieroglyphs_router.post("/confirm", response_model=ConfirmResponse)
async def check_composition_hieroglyph(hieroglyph: str, selected_graphemes: GraphemeRequest, db: AsyncSession = Depends(get_db)):

    confirm = False

    async with db as session:
        # Получаем id частей, из которых состоит иероглиф
        composition_ids = await session.execute(select(Hieroglyph_Parts.id_part_hieroglyph).where(Hieroglyph_Parts.id_hieroglyph == hieroglyph))
        list_composition_id = composition_ids.scalars().all()

        if not list_composition_id:
            raise HTTPException(status_code=404, detail="No hieroglyph parts found")


        # Получаем графемы по каждому id из списка, учитывая повторения
        list_composition = []
        for part_id in list_composition_id:
            grapheme_result = await session.execute(select(Parts_hieroglyphs.part).where(Parts_hieroglyphs.id_part_hieroglyph == part_id))
            grapheme = grapheme_result.scalar()
            if grapheme:
                list_composition.append(grapheme)


        if not list_composition:
            raise HTTPException(status_code=404, detail="No hieroglyphs found")

        # Сравниваем отсортированные списки состава иероглифа и графем выбранных пользователем
        if sorted(list_composition) == sorted(selected_graphemes.graphemes):
            confirm = True

    return ConfirmResponse(confirm=confirm)



'''
этот роут анализирует, 
какие иероглифы в базе данных содержат все переданные графемы, 
и возвращает доступные графемы для каждого иероглифа, исключая те, что были переданы. 
Пользователь отправляет графему (например, "007"), 
сервер находит иероглифы, содержащие эту графему, 
и возвращает список других графем, из которых состоят те же иероглифы, 
но исключает саму введённую графему. 
Этот механизм позволяет пользователю узнать, какие ещё графемы могут быть использованы для составления иероглифа, содержащего заданную графему.:
'''


@hieroglyphs_router.post("/get_available_graphemes", response_model=GraphemeResponse)
async def get_available_graphemes(request: GraphemeRequest, db: AsyncSession = Depends(get_db)):
    """
    Возвращает доступные графемы на основе введенных пользователем.
    """
    if not request.graphemes:
        raise HTTPException(status_code=400, detail="The grapheme list can't be empty")

    async with db as session:
        # Запрос для получения иероглифов, содержащих все введенные графемы
        matching_hieroglyphs = (
            select(Hieroglyph_Parts.id_hieroglyph)
            .select_from(Hieroglyph_Parts)
            .join(Parts_hieroglyphs, Hieroglyph_Parts.id_part_hieroglyph == Parts_hieroglyphs.id_part_hieroglyph)
            .filter(Parts_hieroglyphs.part.in_(request.graphemes))
            .group_by(Hieroglyph_Parts.id_hieroglyph)
            .having(func.count(func.distinct(Parts_hieroglyphs.part)) == len(request.graphemes))
            .subquery()
        )

        # Запрос для получения всех частей подходящих иероглифов
        results = await session.execute(
            select(Hieroglyphs.unicode, Parts_hieroglyphs.part)
            .join(Hieroglyph_Parts, Hieroglyphs.unicode == Hieroglyph_Parts.id_hieroglyph)
            .join(Parts_hieroglyphs, Hieroglyph_Parts.id_part_hieroglyph == Parts_hieroglyphs.id_part_hieroglyph)
            .filter(Hieroglyphs.unicode.in_(
                select(matching_hieroglyphs.c.id_hieroglyph)
            ))
            .order_by(Hieroglyphs.unicode, Hieroglyph_Parts.id_part_hieroglyph)
        )
        results = results.all()

        available_graphemes_set = set()

        # Группируем и обрабатываем результаты по иероглифам
        for _, parts in groupby(results, key=lambda x: x[0]):
            hieroglyph_parts = [p[1] for p in parts]
            # Удаляем каждую введенную графему
            for grapheme in request.graphemes:
                if grapheme in hieroglyph_parts:
                    hieroglyph_parts.remove(grapheme)
            available_graphemes_set.update(hieroglyph_parts)

        # Возвращаем список доступных графем, отсортированный
        return GraphemeResponse(available_graphemes=sorted(list(available_graphemes_set)))

@hieroglyphs_router.post("/get_hieroglyph", response_model=HieroglyphResponse)
async def get_hieroglyph(request: GraphemeRequest, db: AsyncSession = Depends(get_db)):
    """
    Возвращает иероглиф, состоящий из заданных графем.
    """
    if not request.graphemes:
        raise HTTPException(status_code=400, detail="The grapheme list can't be empty")

    grapheme_counts = Counter(request.graphemes)

    async with db as session:
        # Создаем подзапросы для каждой графемы
        subqueries = []
        for grapheme, count in grapheme_counts.items():
            subquery = (
                select(Hieroglyph_Parts.id_hieroglyph)
                .join(
                    Parts_hieroglyphs,
                    Hieroglyph_Parts.id_part_hieroglyph == Parts_hieroglyphs.id_part_hieroglyph
                )
                .filter(Parts_hieroglyphs.part == grapheme)
                .group_by(Hieroglyph_Parts.id_hieroglyph)
                .having(func.count() == count)
            )
            subqueries.append(Hieroglyphs.unicode.in_(subquery))

        # Подзапрос для проверки общего количества частей иероглифа
        total_parts_check = (
            select(Hieroglyph_Parts.id_hieroglyph)
            .group_by(Hieroglyph_Parts.id_hieroglyph)
            .having(func.count() == len(request.graphemes))
        )

        # Основной запрос
        query = (
            select(Hieroglyphs.unicode)
            .filter(and_(*subqueries))
            .filter(Hieroglyphs.unicode.in_(total_parts_check))
            .limit(1)
        )

        result = await session.execute(query)
        unicode_hex = result.scalar()

        if not unicode_hex:
            raise HTTPException(
                status_code=404,
                detail="There is no hieroglyph which contains given graphemes"
            )

        # Преобразование hex-кода в символ Unicode
        try:
            hieroglyph = chr(int(unicode_hex, 16))
            return HieroglyphResponse(hieroglyph=hieroglyph)
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="Hieroglyph code conversion error"
            )