from mimetypes import guess_extension
from os.path import splitext
from shutil import copyfileobj
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import Response

from . import MarkItDown

app = FastAPI()


def convert_upload(upload_file: UploadFile):
    file_extension = None
    ext = None

    # Guess from the mimetype
    file_extension = guess_extension(upload_file.content_type)

    # Read the extension from the filename
    if upload_file.filename:
        base, ext = splitext(upload_file.filename)

    # Save the file locally to a temporary file. It will be deleted before this function exits
    with NamedTemporaryFile(suffix=ext) as temp:
        copyfileobj(upload_file.file, temp)
        temp.flush()
        upload_file.file.close()

        return MarkItDown().convert(temp.name, file_extension=file_extension)


@app.post("/convert")
def convert(request: Request, file: UploadFile) -> Response:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        result = convert_upload(file)

        if request.headers.get("Accept") == "application/json":
            return result
        else:
            return Response(content=result.text_content, media_type="text/markdown")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
