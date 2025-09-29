from pydantic import BaseModel

class TechnicalTodo(BaseModel):
	id: int
	title: str
	description: str
	completed: bool
