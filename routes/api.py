import os
import zipfile
import tempfile
import logging
from http.client import responses

from fastapi import APIRouter, File, UploadFile, HTTPException
from docx import Document

from DTO.Requests.output_request import OutputRequest
from DTO.Requests.todo_list_request import TodoListRequest
from DTO.Requests.parser_request import ParserRequest, ParseProjectRequest
from controllers.build_output_controller import BuildOutputController
from controllers.llm_controller import LLMController
from controllers.parser_controller import ParserController

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])

@router.get("/")
def read_root():
	return {"Hello": "World"}

@router.post("/import-transcript/{folder_id}")
async def import_transcript(folder_id: str, file: UploadFile = File(...)):
	logger.info(f"[IMPORT-TRANSCRIPT] Starting import for folder_id={folder_id}, filename={file.filename}")
	try:
		folder_path = os.path.join(tempfile.gettempdir(), folder_id)
		os.makedirs(folder_path, exist_ok=True)
		logger.debug(f"[IMPORT-TRANSCRIPT] Created temp folder: {folder_path}")
		
		file_path = os.path.join(folder_path, file.filename)
		content = await file.read()
		logger.debug(f"[IMPORT-TRANSCRIPT] Read {len(content)} bytes from uploaded file")

		with open(file_path, "wb") as f:
			f.write(content)
		logger.debug(f"[IMPORT-TRANSCRIPT] Wrote file to: {file_path}")
		
		text_content = ""
		filename_lower = file.filename.lower()
		
		if filename_lower.endswith('.txt'):
			logger.info(f"[IMPORT-TRANSCRIPT] Processing .txt file")
			try:
				text_content = content.decode('utf-8')
				logger.debug(f"[IMPORT-TRANSCRIPT] Decoded as UTF-8")
			except UnicodeDecodeError:
				text_content = content.decode('latin-1')
				logger.warning(f"[IMPORT-TRANSCRIPT] Failed UTF-8, decoded as latin-1")
		elif filename_lower.endswith('.docx'):
			logger.info(f"[IMPORT-TRANSCRIPT] Processing .docx file")
			doc = Document(file_path)
			paragraphs = [paragraph.text for paragraph in doc.paragraphs]
			logger.debug(f"[IMPORT-TRANSCRIPT] Extracted {len(paragraphs)} paragraphs from docx")
			non_empty_paragraphs = [p for p in paragraphs if p.strip()]
			text_content = '\n'.join(non_empty_paragraphs)
			logger.debug(f"[IMPORT-TRANSCRIPT] Filtered to {len(non_empty_paragraphs)} non-empty paragraphs")
			if len(text_content) == 0:
				logger.error(f"[IMPORT-TRANSCRIPT] No text extracted from docx file!")
		else:
			logger.error(f"[IMPORT-TRANSCRIPT] Unsupported file type: {file.filename}")
			raise HTTPException(status_code=400, detail="Only .txt and .docx files are supported")
		
		logger.info(f"[IMPORT-TRANSCRIPT] Successfully imported transcript, length={len(text_content)} chars")
		return {"name": file.filename, "content": text_content}

	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"[IMPORT-TRANSCRIPT] Error importing transcript: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-project/{folder_id}")
async def import_zip(folder_id: str, file: UploadFile = File(...)):
	logger.info(f"[IMPORT-PROJECT] Starting import for folder_id={folder_id}, filename={file.filename}")
	try:
		if not file.filename.lower().endswith(".zip"):
			logger.error(f"[IMPORT-PROJECT] Invalid file type: {file.filename}")
			raise HTTPException(status_code=400, detail="Only .zip files are allowed")

		folder_path = os.path.join(tempfile.gettempdir(), folder_id)
		os.makedirs(folder_path, exist_ok=True)
		logger.debug(f"[IMPORT-PROJECT] Created temp folder: {folder_path}")

		zip_path = os.path.join(folder_path, file.filename)
		with open(zip_path, "wb") as f:
			content = await file.read()
			f.write(content)
		logger.debug(f"[IMPORT-PROJECT] Wrote zip file: {zip_path}, size={len(content)} bytes")

		with zipfile.ZipFile(zip_path, "r") as zip_ref:
			file_list = zip_ref.namelist()
			logger.debug(f"[IMPORT-PROJECT] Extracting {len(file_list)} files from zip")
			zip_ref.extractall(folder_path)
		
		logger.info(f"[IMPORT-PROJECT] Successfully extracted project to {folder_path}")
		return {"name": file.filename}

	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"[IMPORT-PROJECT] Error importing project: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-todolist")
async def generate_todolist(todo_list_request: TodoListRequest):
	logger.info(f"[GENERATE-TODO] Starting todolist generation")
	logger.debug(f"[GENERATE-TODO] Transcript length: {len(todo_list_request.transcript)} chars")
	logger.debug(f"[GENERATE-TODO] Parsed project length: {len(todo_list_request.parsed_project)} chars")
	
	try:
		controller = LLMController()
		logger.debug(f"[GENERATE-TODO] LLM Controller initialized")
		
		response = controller.transcript_to_technical_todo(todo_list_request)
		logger.debug(f"[GENERATE-TODO] Received response from controller")
		
		if not response.context or not response.technical_todo:
			logger.error(f"[GENERATE-TODO] Response missing required fields - context: {bool(response.context)}, technical_todo: {bool(response.technical_todo)}")
			raise HTTPException(status_code=500, detail="error occured while generating the todolist")
		
		logger.info(f"[GENERATE-TODO] Successfully generated todolist - context: {len(response.context)} chars, todo: {len(response.technical_todo)} chars")
		return {"context": response.context, "technical_todolist": response.technical_todo, "clarifications": response.clarifications}
	
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"[GENERATE-TODO] Error generating todolist: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-output")
async def build_output(output_request: OutputRequest):
	logger.info(f"[BUILD-OUTPUT] Starting output build")
	controller = BuildOutputController()
	try:
		result = controller.store(output_request)
		logger.info(f"[BUILD-OUTPUT] Output stored successfully at: {result}")
		return {"message": "Output stored successfully", "path": result}
	except Exception as e:
		logger.error(f"[BUILD-OUTPUT] Error storing output: {str(e)}", exc_info=True)
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
	logger.info(f"[PARSE-PROJECT] Starting project parse for path={parse_request.project_path}")
	controller = ParserController()
	try:
		response = controller.parse_project(parse_request)
		# Response is a Pydantic model, access attribute directly
		parsed_length = len(response.parsed_project) if hasattr(response, 'parsed_project') else 0
		logger.info(f"[PARSE-PROJECT] Successfully parsed project, response length: {parsed_length} chars")
		return response
	except ValueError as e:
		logger.error(f"[PARSE-PROJECT] Validation error: {str(e)}")
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		logger.error(f"[PARSE-PROJECT] Error parsing project: {str(e)}", exc_info=True)
		raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-llm-api")
def test_llm_api():
	try:
		controller = LLMController()
		response = controller.test_api_call()
		return {"response": response}
	except Exception as e:
		print(f"Error testing LLM API: {str(e)}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=str(e))
