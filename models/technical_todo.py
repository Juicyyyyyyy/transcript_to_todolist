from pydantic import BaseModel

class technicalTodo(BaseModel):
	id: int
	title: str
	description: str
	completed: bool