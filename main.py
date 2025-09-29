from os import mkdir
import uuid
from fastapi import FastAPI
from routes.api import router

app = FastAPI()

app.include_router(router)

upload_id = str(uuid.uuid4())

upload_path = f"/tmp/{upload_id}"

mkdir(upload_path)
