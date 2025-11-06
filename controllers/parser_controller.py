import logging
from DTO.Requests.parser_request import ParserRequest, ParseProjectRequest
from DTO.Responses.parser_response import ParserResponse, ParsedProjectResponse
from services.parser_service import ParserService


class ParserController:
	"""Controller for handling parser operations"""

	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.debug("[PARSER-CONTROLLER] Initializing Parser Controller")
		self.service = ParserService()

	def extract_symbols(self, request: ParserRequest) -> ParserResponse:
		"""Extract symbols from a parsed project file"""
		self.logger.info(f"[PARSER-CONTROLLER] Extracting symbols from file: {request.file_path}")
		self.logger.debug(f"[PARSER-CONTROLLER] Project path: {request.project_path}")
		
		try:
			# First, parse the project
			self.service.set_ast(request.project_path)
			self.logger.debug(f"[PARSER-CONTROLLER] AST set for project")
			
			# Then extract symbols from the requested file
			symbols = self.service.extract_symbols(request.file_path)
			self.logger.info(f"[PARSER-CONTROLLER] Successfully extracted {len(symbols.get('classes', []))} symbols from {request.file_path}")
			
			return ParserResponse(
				file=symbols["file"],
				classes=symbols["classes"]
			)
		except Exception as e:
			self.logger.error(f"[PARSER-CONTROLLER] Error extracting symbols: {str(e)}", exc_info=True)
			raise
	
	def parse_project(self, request: ParseProjectRequest) -> ParsedProjectResponse:
		"""Parse entire project and return all symbols as a formatted string"""
		self.logger.info(f"[PARSER-CONTROLLER] Parsing entire project at: {request.project_path}")
		
		try:
			# Parse the project
			asts = self.service.set_ast(request.project_path)
			self.logger.info(f"[PARSER-CONTROLLER] Parsed {len(asts)} files")
			
			# Extract all symbols and format for OpenAI
			parsed_content = self.service.extract_all_symbols()
			self.logger.info(f"[PARSER-CONTROLLER] Generated parsed content: {len(parsed_content)} chars")
			
			return ParsedProjectResponse(parsed_project=parsed_content)
		except Exception as e:
			self.logger.error(f"[PARSER-CONTROLLER] Error parsing project: {str(e)}", exc_info=True)
			raise


