import logging
from DTO.Requests.todo_list_request import TodoListRequest
from DTO.Responses.llm_response import LLMResponse
from services.llm_service import LLMService

class LLMController:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.debug("[LLM-CONTROLLER] Initializing LLM Controller")
		self.service = LLMService()
		self.logger.debug("[LLM-CONTROLLER] LLM Service initialized")

	def transcript_to_technical_todo(self, request: TodoListRequest) -> LLMResponse:
		self.logger.info("[LLM-CONTROLLER] Processing transcript to technical todo request")
		try:
			response = self.service.transcript_to_technical_todo(request)
			self.logger.info("[LLM-CONTROLLER] Successfully processed request")
			return response
		except Exception as e:
			self.logger.error(f"[LLM-CONTROLLER] Error in transcript_to_technical_todo: {str(e)}", exc_info=True)
			raise

	def test_api_call(self):
		self.logger.info("[LLM-CONTROLLER] Running LLM API test")
		try:
			response = self.service.test_api_call()
			self.logger.info("[LLM-CONTROLLER] API test successful")
			return response
		except Exception as e:
			self.logger.error(f"[LLM-CONTROLLER] API test failed: {str(e)}", exc_info=True)
			raise
