from fastapi import FastAPI, Depends, status, HTTPException, Response
from pydantic import BaseModel, BaseSettings
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import bcrypt
from passlib.context import CryptContext
import secrets
from typing import Optional


class Settings(BaseSettings):
    MODE: str = "DEV"
    DOCS_USER: Optional[str] = None
    DOCS_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(
    title="Protected Docs API",
    docs_url=None,  # Отключаем стандартные docs
    redoc_url=None,  # Отключаем стандартные redoc
    openapi_url=None if settings.MODE == "PROD" else "/openapi.json",  # Отключаем в PROD
)
security = HTTPBasic()

context = CryptContext(schemes=['bcrypt'])


class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

USER_DATA = []

def get_user_db(username:str):
    for user in USER_DATA:
        if secrets.compare_digest(user.username, username):
            return user
    
    return None

async def auth_user(response: Response, cred: HTTPBasicCredentials = Depends(security)):
    user = get_user_db(cred.username)
    if user is None or not context.verify(cred.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Unauthorized')

    return user


@app.get('/users')
def get_users():
    return USER_DATA


@app.post('/register')
async def register_user(user: User):
    user_password = context.hash(user.password)
    hash_user = UserInDB(username=user.username, hashed_password=user_password)
    USER_DATA.append(hash_user)
    return {'message': 'success register', 'user': hash_user}

@app.get("/login")
async def read_root(user=Depends(auth_user)):
    return {"message": "You got my secret, welcome", 'user': user}


@app.get("/logout")
async def force_logout(response: Response):
    # Отправляем специальный заголовок для сброса Basic Auth
    response.headers["WWW-Authenticate"] = 'Basic realm="Logged Out"'
    return {"message": "You have been logged out"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('tasts2:app', reload=True)
