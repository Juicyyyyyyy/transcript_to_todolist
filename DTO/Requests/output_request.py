from pydantic import BaseModel

class OutputRequest(BaseModel):
	context: str
	technical_todo: str
	clarifications: str
