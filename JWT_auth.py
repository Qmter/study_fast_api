from fastapi import FastAPI, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig
from pydantic import BaseModel

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = 'SOME_SECRET_KEY_FROM_YAROSLAV'
config.JWT_ACCESS_COOKIE_NAME = "yara_token"
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_COOKIE_CSRF_PROTECT = False 

security = AuthX(config=config)

class UserLoginShema(BaseModel):
    username: str 
    password: str


@app.post('/login')
def login(creds: UserLoginShema, response: Response):
    if creds.username == 'yara' and creds.password == 'yara':
        token = security.create_access_token(uid='123')
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail='incorrect username or password ')
          
    
@app.post('/protected', dependencies=[Depends(security.access_token_required)])
def protected(): 
    return {'date': 'wtf '}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('JWT_auth:app', reload=True)