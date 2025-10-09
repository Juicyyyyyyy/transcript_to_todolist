from pydantic import BaseModel


class ParserRequest(BaseModel):
	"""Request model for extracting symbols from a project file"""
	project_path: str
	file_path: str


class ParseProjectRequest(BaseModel):
	"""Request model for parsing an entire project"""
	project_path: str


