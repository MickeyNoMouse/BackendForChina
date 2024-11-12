from fastapi import APIRouter, HTTPException
from typing import Union
from models.models import TokenDetail, TranslationRequest, TranslationResponse
from jieba import cut
from dictionary import CHINESE_DICT

translation_router = APIRouter(prefix="/translation", tags=["Перевод"])

def translate_detailed(text: str) -> Union[TranslationResponse, TokenDetail]:
    """
    Обработка китайского текста и возврат подробной информации о каждом токене
    """
    try:
        # Если текст состоит из одного слова, возвращаем информацию только о нем
        if text in CHINESE_DICT:
            pinyin, meanings = CHINESE_DICT[text]
            return TokenDetail(token=text, pinyin=pinyin, meanings=meanings)

        # Разбиение текста на токены с помощью jieba
        tokens = cut(text)
        translated_tokens = []

        # Обработка каждого токена
        for token in tokens:
            if token.strip():  # Пропуск пустых токенов
                if token in CHINESE_DICT:
                    # Если токен найден в словаре, получаем его пиньинь и значения
                    pinyin, meanings = CHINESE_DICT[token]
                    translated_tokens.append(
                        TokenDetail(
                            token=token,
                            pinyin=pinyin,
                            meanings=meanings
                        )
                    )
                else:
                    # Если токен не найден, добавляем его без перевода
                    translated_tokens.append(
                        TokenDetail(
                            token=token,
                            pinyin="",
                            meanings=[]
                        )
                    )

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