import os
import zipfile
from http.client import responses

from fastapi import APIRouter, File, UploadFile, HTTPException
from docx import Document

from DTO.Requests.output_request import OutputRequest
from DTO.Requests.todo_list_request import TodoListRequest
from DTO.Requests.parser_request import ParserRequest, ParseProjectRequest
from controllers.build_output_controller import BuildOutputController
from controllers.open_ai_controller import OpenAiController
from controllers.parser_controller import ParserController

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/")
def read_root():
	return {"Hello": "World"}

@router.post("/import-transcript/{folder_id}")
async def import_transcript(folder_id: str, file: UploadFile = File(...)):
	try:
		folder_path = os.path.join("/tmp", folder_id)
		os.makedirs(folder_path, exist_ok=True)
		
		file_path = os.path.join(folder_path, file.filename)
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

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-todolist")
async def generate_todolist(todo_list_request: TodoListRequest):
	try:
		controller = OpenAiController()
		response = controller.transcript_to_technical_todo(todo_list_request)
		if not response.context or not response.technical_todo:
			raise HTTPException(status_code=500, detail="error occured while generating the todolist")
		
		return {"context": response.context, "technical_todolist": response.technical_todo, "clarifications": response.clarifications}
	
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-output")
async def build_output(output_request: OutputRequest):
	controller = BuildOutputController()
	try:
		result = controller.store(output_request)
		return {"message": "Output stored successfully", "path": result}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-symbols")
async def extract_symbols(parser_request: ParserRequest):
	"""Extract symbols (classes, methods, properties) from a project file"""
	controller = ParserController()
	try:
		response = controller.extract_symbols(parser_request)
		return response
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-project")
async def parse_project(parse_request: ParseProjectRequest):
	"""Parse entire project and return all symbols as a formatted string for OpenAI"""
	controller = ParserController()
	try:
		response = controller.parse_project(parse_request)
		return response
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
