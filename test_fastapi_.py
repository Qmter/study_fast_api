from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class BookModel(BaseModel):
    id: int
    title: str
    author: str

class AddBookModel(BaseModel):
    title: str
    author: str


books = [
    {
        'id': 1,
        'title': 'book1',
        'author': 'author1'
    },
    {
        'id': 2,
        'title': 'book2',
        'author': 'author2'
    }
]


@app.get('/books')
def get_books():
    return books


@app.post('/books')
def add_book(book: AddBookModel):
    book_id = len(books) + 1
    books.append({
    'id': book_id,
    'title': book.title,
    'author': book.author
    })
    return {"add book": 'success'}



@app.put('/books/{book_id}')
def change_book(book_id: int, book: AddBookModel):
    for i in books:
        if i['id'] == book_id:
            i['author'] = book.author
            i['title'] = book.title
            return {"change": "success"}
    return HTTPException(status_code=404, detail="Book not found!")


@app.delete('/books/{book_id}')
def del_book(book_id: int):
    for i in books:
        if i['id'] == book_id:
            books.remove(i)
            return {"delete": "success"}
    return HTTPException(status_code=404, detail="Book not found!")


@app.post('/files')
def upload_file(upload_file: UploadFile):
    file = upload_file.file
    filename = upload_file.filename
    with open(f'{filename}', 'wb') as f:
        f.write(file.read())

@app.get('/files/{filename}')
def get_file(filename: str):
    return FileResponse(filename)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('test_fastapi_:app', reload=True)
