from DTO.Requests.todo_list_request import TodoListRequest
from DTO.Responses.open_ai_response import OpenAiResponse
from services.openai_service import OpenAiService

class OpenAiController:
	def __init__(self):
		self.service = OpenAiService()

	def transcript_to_technical_todo(self, request: TodoListRequest) -> OpenAiResponse:
		return self.service.transcript_to_technical_todo(request)
