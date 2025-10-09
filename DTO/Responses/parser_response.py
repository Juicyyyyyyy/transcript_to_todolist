from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class MethodInfo(BaseModel):
	"""Information about a class method"""
	name: Optional[str]
	return_type: Optional[str] = None
	
	class Config:
		populate_by_name = True
		
	def __init__(self, **data):
		# Handle 'return' field mapping to 'return_type'
		if 'return' in data:
			data['return_type'] = data.pop('return')
		super().__init__(**data)


class ClassInfo(BaseModel):
	"""Information about a class"""
	class_name: Optional[str] = None
	extends: Optional[str] = None
	properties: List[str] = []
	methods: List[MethodInfo] = []
	
	class Config:
		populate_by_name = True
		
	def __init__(self, **data):
		# Handle 'class' field mapping to 'class_name'
		if 'class' in data:
			data['class_name'] = data.pop('class')
		super().__init__(**data)


class ParserResponse(BaseModel):
	"""Response model for symbol extraction"""
	file: str
	classes: List[ClassInfo]


class ParsedProjectResponse(BaseModel):
	"""Response model for parsed project"""
	parsed_project: str


