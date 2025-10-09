from pydantic import BaseModel

class TodoListRequest(BaseModel):
	parsed_project: str
	transcript: str
