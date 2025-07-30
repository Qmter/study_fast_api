from fastapi import FastAPI, Response, Form, File, UploadFile, Query, Path, Body, Cookie
import models
from typing import Annotated

app = FastAPI()

feedbacks = []

fake_clients = [
    {
        "id": 1,
        "name": "Иванов Алексей",
        "email": "ivanov.alex@example.com",
        "phone": "79161234567"
    },
    {
        "id": 2,
        "name": "Петрова Мария",
        "email": "petrova.m@mail.ru",
        "phone": "79037654321"
    },
    {
        "id": 3,
        "name": "Сидоров Дмитрий",
        "email": "sidorov.dmitry@gmail.com",
        "phone": None
    },
    {
        "id": 4,
        "name": "Кузнецова Анна",
        "email": "anna.k@yandex.ru",
        "phone": "74951234567"
    },
    {
        "id": 5,
        "name": "Смирнов Владимир",
        "email": "v.smirnov@company.com",
        "phone": "375291234567"
    },
    {
        "id": 6,
        "name": "Фролова Екатерина",
        "email": "ekaterina.f@outlook.com",
        "phone": None
    },
    {
        "id": 7,
        "name": "Николаев Артем",
        "email": "artem.n@protonmail.com",
        "phone": "77015556677"
    },
    {
        "id": 8,
        "name": "Григорьева Ольга",
        "email": "olga.g@hotmail.com",
        "phone": "79081234567"
    },
    {
        "id": 9,
        "name": "Павлов Игорь",
        "email": "pavlov.igor@bk.ru",
        "phone": None
    },
    {
        "id": 10,
        "name": "Козлова Виктория",
        "email": "v.kozlova@inbox.ru",
        "phone": "79261234567"
    }
]

@app.post('/feedbacks', response_model=models.feedbackResponse, description='отправка фидбэка на сервер', name='пост запрос', tags=['FEEDBACK'])
async def add_feedback(feedback: models.Feedback, is_premium: bool = False):
    if is_premium:
        feedbacks.append(feedback)
        return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён. Ваш отзыв будет рассмотрен в приоритетном порядке.", 'feedback': feedback}
    else:
        feedbacks.append(feedback)
        return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён.", 'feedback': feedback}


@app.get('/feedbacks', description='получение фидбэка с сервера', name='гет запрос', tags=['FEEDBACK'])
async def get_feedbacks(limit: int = 10):
    return feedbacks[:limit]

@app.post("/multiple-files/", name='загрузка на сервер нескольких файлов', tags=['FILES'])
async def upload_multiple_files(upload_files: list[UploadFile]):
    for upload_file in upload_files:
        file = upload_file.file
        filename = upload_file.filename
        with open(f'{filename}', 'wb') as f:
            f.write(file.read())

    return {"filenames": [file.filename for file in upload_files]}


@app.post("/file/", name='загрузка на сервер 1 файла по чанкам', tags=['FILES'])
async def upload_file(file: UploadFile):
    with open(f'{file.filename}', 'wb') as f:
        while chunk := await file.read(1024):
            f.write(chunk)
    return {"filenames": file.filename}

@app.post("/submit/", name='отправка данных на сервер через html Form', tags=['FORM'])
async def submit_form(
    username: str = Form(...), 
    password: str = Form(...)
):
    return {"username": username, "password_length": password}


@app.get('/clients', response_model=models.UserResponse, name='получение клиентов с start и limit', tags=['clients'])
async def get_client(
    start: int = Query(0, ge=0),
    limit: int = Query(5, le=20)
    ):
    return {'client': fake_clients[start: start + limit]}


@app.get('/clients/{client_id}', response_model=models.ClientResponse_noid, name='получение клиентов через path', tags=['clients'])
async def get_client_with_path(client_id: int = Path(..., ge=0, le=10)):
    for i in fake_clients:
        if i['id'] == client_id:
            return i
        
@app.post('/clients/', response_model=models.ClientResponse_noid, name='отправить на сервер клиента через боди', tags=['clients'])
async def add_client(client_: Annotated[models.ClientResponse, Body()]):
    fake_clients.append(client_)
    return client_



@app.post('/create_user', name='создать юзера', tags=['clients'])
async def create_client(client: models.UserCreate):
    fake_clients.append(client)
    return client

        

@app.get("/", tags=['COOKIES'])
async def root(last_visit = Cookie()):
    return {"last visit": last_visit}

@app.get('/get_cookie', tags=['COOKIES'])
async def set_cookie(response: Response):
    response.set_cookie(key="user_id", value="12345", max_age=3600, httponly=True)
    return {"message": "Cookie has been set!"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)