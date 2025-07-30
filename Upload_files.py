from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse


app = FastAPI() 


@app.post('/files')
async def upload_file(upload_file: UploadFile):
    file = upload_file.file
    filename = upload_file.filename
    with open(f'{filename}', 'wb') as f:
        f.write(file.read())

@app.post('/multiply_files')
async def upload_files(upload_files: list[UploadFile]):
    for upload_file in upload_files:
        file = upload_file.file
        filename = upload_file.filename
        with open(f'{filename}', 'wb') as f:
            f.write(file.read())

@app.get('/get_file/{filename}')
async def get_file(filename: str):
    return FileResponse(filename)

def iterfile(filename: str):
    with open(filename, 'rb') as f:
        while chunk := f.read(1024*1024):
            yield chunk

@app.get('/files/streaming/{filename}')
async def get_streaming_file(filename: str):
    return StreamingResponse(iterfile(filename), media_type='video/mp4')




if __name__ == '__main__':
    import uvicorn
    uvicorn.run('Upload_files:app', reload=True)