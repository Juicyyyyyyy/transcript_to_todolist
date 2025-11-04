from DTO.Requests.todo_list_request import TodoListRequest
from DTO.Responses.llm_response import LLMResponse
from services.llm_service import LLMService

class LLMController:
	def __init__(self):
		self.service = LLMService()

	def transcript_to_technical_todo(self, request: TodoListRequest) -> LLMResponse:
		return self.service.transcript_to_technical_todo(request)

	def test_api_call(self):
		return self.service.test_api_call()
