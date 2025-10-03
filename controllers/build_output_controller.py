from DTO.Requests.output_request import OutputRequest
from services.build_output_service import BuildOutputService


class BuildOutputController:

	def __init__(self):
		self.service = BuildOutputService()

	def store(self, request: OutputRequest):
		return self.service.store_and_return_path(request)
