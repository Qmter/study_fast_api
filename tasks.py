from fastapi import FastAPI, Response, HTTPException, Depends, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import datetime
from pydantic import BaseModel
import jwt
from typing import Optional, Dict, Annotated
from passlib.context import CryptContext

class User(BaseModel):
    username: str
    password: str


myhash = CryptContext(schemes=['bcrypt'], deprecated="auto")

oauth_shemas_login = OAuth2PasswordBearer(tokenUrl='/login')
oauth_shemas_refresh = OAuth2PasswordBearer(tokenUrl='/refresh')



SECRET_KEY_ACCESS = "access_key_secret"  
SECRET_KEY_REFRESH = "refresh_key_secret"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 3


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    retry_after = 60
    return Response(
        content="Too Many Requests",
        status_code=429,
        headers={"Retry-After": str(retry_after)}
    )

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


USER_DB = []
REFRESH_TOKENS = []


def create_access_token(data: Dict):
    
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    to_encode.update({'type': 'access'})


    print(to_encode)
    return jwt.encode(to_encode, SECRET_KEY_ACCESS, algorithm=ALGORITHM)


def create_refresh_token(data: Dict):
    
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    to_encode.update({'type': 'refresh'})

    print(to_encode)
    return jwt.encode(to_encode, SECRET_KEY_REFRESH, algorithm=ALGORITHM)


def get_user_from_token(token: str = Depends(oauth_shemas_login)):

    try:

        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=[ALGORITHM])

        username = payload.get('sub')
    
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def get_user(username: str):
    for user in USER_DB:
        if user.get('username') == username:
            return user
        
    return None 

def get_fromDB_refresh_token(username: str):
    for token in REFRESH_TOKENS:
        if username in token:
            return token[username]
    return None

@app.get('/')
def get():
    return REFRESH_TOKENS
    
@app.post('/register')
@limiter.limit("1/minute")
def reg_user(user: User, request: Request):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail='Пользователь уже существует!')
    
    hash_pass = myhash.hash(user.password)
    USER_DB.append({'username': user.username, 'password': hash_pass})

    return {'success registration': user}


@app.post('/login')
@limiter.limit("5/minute")
def login_user(user: User, response: Response, request: Request):
    for user_db in USER_DB:
        if user.username == user_db.get('username') and myhash.verify(user.password, user_db.get('password')):
            access_token = create_access_token({'sub': user.username})
            refresh_token = create_refresh_token({'sub': user.username})

            
            response.set_cookie(key='access_token', value=access_token, expires=60*1,)
            response.set_cookie(key='refresh_token', value=refresh_token, expires=60*3,)

            REFRESH_TOKENS.append({user.username: refresh_token})

            return {"access_token": access_token, 'refresh_token': refresh_token, "token_type": "bearer"}
    
        
    raise HTTPException(status_code=404, detail='User not found')



@app.post('/refresh')
@limiter.limit("5/minute")
async def get_refresh_token(response: Response, request: Request, refresh_token: Annotated[str | None, Cookie()] = None):
    try:
        if not refresh_token:
            raise HTTPException(status_code=401, detail='refresh token no123t found')
        
        payload = jwt.decode(refresh_token, SECRET_KEY_REFRESH, algorithms=[ALGORITHM])
        username = payload.get('sub')

        ref_token_DB = get_fromDB_refresh_token(str(username))


        print(payload.get('type'), 'type')
        print(ref_token_DB, 'ref_token')
        if ref_token_DB is None or ref_token_DB != refresh_token:
            raise HTTPException(status_code=401, detail='Invalid or revoked refresh token')
        
        new_access_token = create_access_token({'sub':username})
        new_refresh_token = create_refresh_token({'sub': username})
        
        for token in REFRESH_TOKENS:
            if token.get('username') == username:
                token[username] = new_refresh_token
        
        response.set_cookie(key='access_token', value=new_access_token, expires=60*1,)
        response.set_cookie(key='refresh_token', value=new_refresh_token, expires=60*3,)

        return {'access_token': new_access_token, 'refresh_token': new_refresh_token}




    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
 
    
    

@app.get('/protected_resource')
def get_prot_res(access_token: Annotated[str | None, Cookie()] = None):
    username = get_user_from_token(str(access_token))
    user = get_user(username)

    if user is None:
        raise HTTPException(status_code=403, detail='you have not access')
    else:
        return {'success': 'you was authorized!', 'user': user}








if __name__ == '__main__':
    

    import uvicorn
    uvicorn.run('tasks:app', reload=True)