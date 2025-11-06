import logging
from DTO.Requests.output_request import OutputRequest
from services.build_output_service import BuildOutputService


class BuildOutputController:

	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.debug("[BUILD-OUTPUT-CONTROLLER] Initializing Build Output Controller")
		self.service = BuildOutputService()

	def store(self, request: OutputRequest):
		self.logger.info("[BUILD-OUTPUT-CONTROLLER] Storing output files")
		try:
			result = self.service.store_and_return_path(request)
			self.logger.info(f"[BUILD-OUTPUT-CONTROLLER] Successfully stored output at {result}")
			return result
		except Exception as e:
			self.logger.error(f"[BUILD-OUTPUT-CONTROLLER] Error storing output: {str(e)}", exc_info=True)
			raise
