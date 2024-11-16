from fastapi import APIRouter, HTTPException
from typing import Union
from models.models import TokenDetail, TranslationRequest, TranslationResponse
from jieba import cut
from dictionary import CHINESE_DICT

translation_router = APIRouter(prefix="/translation", tags=["Перевод"])

def get_token_detail(token: str) -> TokenDetail:
    """
    Возвращает подробную информацию о токене, если он найден в словаре.
    Если токен не найден, возвращает объект с пустыми значениями.
    """
    pinyin, meanings = CHINESE_DICT.get(token, ("", []))
    return TokenDetail(token=token, pinyin=pinyin, meanings=meanings)

def translate_detailed(text: str) -> Union[TranslationResponse, TokenDetail]:
    """
    Обработка китайского текста и возврат подробной информации о каждом токене.
    """
    try:
        # Пытаемся перевести текст как один токен
        single_token_result  = get_token_detail(text)

        # Если полученный результат не пустой, возвращаем его
        if single_token_result.pinyin:
            return single_token_result

        # Разбиение текста на токены с помощью jieba и обработка каждого токена
        tokens = (token.strip() for token in cut(text))
        translated_tokens = [get_token_detail(token) for token in tokens if token]

        return TranslationResponse(tokens=translated_tokens)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для перевода текста и получения информации об отдельном слове
@translation_router.post("/translate/", response_model=Union[TranslationResponse, TokenDetail])
async def translate(request: TranslationRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Предоставлен пустой текст")

    if len(request.text) > 50:
        raise HTTPException(status_code=400, detail="Текст слишком длинный")

    return translate_detailed(request.text)