import os
import zipfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from docx import Document

from controllers.open_ai_controller import OpenAiController

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/")
def read_root():
	return {"Hello": "World"}

@router.post("/import-transcript{transcript}{folder_id}")
async def import_transcript(folder_id: str, file: UploadFile = File(...)):
	try:
		file_path = f"/tmp/{folder_id}"

		with open(file_path, "wb") as f:
			content = await file.read()
			f.write(content)

		return {"name": file.filename}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-project/{folder_id}")
async def import_zip(folder_id: str, file: UploadFile = File(...)):
	try:
		if not file.filename.lower().endswith(".zip"):
			raise HTTPException(status_code=400, detail="Only .zip files are allowed")

		folder_path = os.path.join("/tmp", folder_id)
		os.makedirs(folder_path, exist_ok=True)

		zip_path = os.path.join(folder_path, file.filename)
		with open(zip_path, "wb") as f:
			content = await file.read()
			f.write(content)

		with zipfile.ZipFile(zip_path, "r") as zip_ref:
			zip_ref.extractall(folder_path)

		return {"name": file.filename}

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
