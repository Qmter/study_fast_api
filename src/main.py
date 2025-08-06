from fastapi import FastAPI, Query
from models import ResponseUser, CreateUser 
from exceptions import (  
    CustomNotFoundException, 
    CustomUnauthorizedException,
    register_exception_handlers)

app = FastAPI()



users = {'yara': {'username': 'yara', 'password': 'yara'}, 'iva': {'username': 'iva', 'password': 'iva'}}

register_exception_handlers(app)

def check_user(username_check: str):
    if username_check not in users:
        raise CustomNotFoundException(status_code=404, detail='User Not Found', message='Try to change username')
    return users[username_check]

@app.post('/register', response_model=ResponseUser)
async def register(user: CreateUser):
    users[user.username] = {'username': user.username, 'password': user.password}
    return {'username': user.username}


@app.post('/login')
async def login(user: CreateUser):
    user_db = check_user(user.username)
    
    if user_db.get('password') != user.password:
        raise CustomUnauthorizedException(status_code=401, detail='You are not authorized', message='Invalid password')
    
    return {'success login': f'{user.username}, Welcome!'}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)