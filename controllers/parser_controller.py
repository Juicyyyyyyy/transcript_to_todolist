from DTO.Requests.parser_request import ParserRequest, ParseProjectRequest
from DTO.Responses.parser_response import ParserResponse, ParsedProjectResponse
from services.parser_service import ParserService


class ParserController:
	"""Controller for handling parser operations"""

	def __init__(self):
		self.service = ParserService()

	def extract_symbols(self, request: ParserRequest) -> ParserResponse:
		"""Extract symbols from a parsed project file"""
		# First, parse the project
		self.service.set_ast(request.project_path)
		
		# Then extract symbols from the requested file
		symbols = self.service.extract_symbols(request.file_path)
		
		return ParserResponse(
			file=symbols["file"],
			classes=symbols["classes"]
		)
	
	def parse_project(self, request: ParseProjectRequest) -> ParsedProjectResponse:
		"""Parse entire project and return all symbols as a formatted string"""
		# Parse the project
		self.service.set_ast(request.project_path)
		
		# Extract all symbols and format for OpenAI
		parsed_content = self.service.extract_all_symbols()
		
		return ParsedProjectResponse(parsed_project=parsed_content)


