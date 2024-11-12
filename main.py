from fastapi import FastAPI
from routes.users import users_router
from routes.hieroglyphs import hieroglyphs_router
from routes.translation import translation_router
app = FastAPI()

app.include_router(users_router)
app.include_router(hieroglyphs_router)
app.include_router(translation_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)