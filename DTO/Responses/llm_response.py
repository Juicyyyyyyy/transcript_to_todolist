import json
import logging


class LLMResponse:
	def __init__(self, response):
		self.logger = logging.getLogger(__name__)
		self.logger.debug("Creating LLMResponse object")
		
		try:
			# Extract content from LlamaIndex response
			if hasattr(response, 'message') and hasattr(response.message, 'content'):
				content = response.message.content
				self.logger.debug("Extracted content from response.message.content")
			elif hasattr(response, 'content'):
				content = response.content
				self.logger.debug("Extracted content from response.content")
			else:
				content = str(response)
				self.logger.warning("Using string representation of response as content")
			
			self.logger.debug(f"Raw content length: {len(content)} characters")
			
			# Parse JSON content
			try:
				_response_json = json.loads(content)
				self.logger.debug("Successfully parsed JSON content")
			except json.JSONDecodeError as e:
				self.logger.error(f"Failed to parse JSON content: {str(e)}")
				self.logger.error(f"Content preview: {content[:200]}...")
				raise ValueError(f"Invalid JSON in LLM response: {str(e)}")
			
			# Extract required fields with validation
			self.context = self._extract_field(_response_json, "contexte", "Context")
			self.technical_todo = self._extract_field(_response_json, "technical_todolist", "Technical Todo List")
			self.clarifications = self._extract_field(_response_json, "clarifications_requises", "Clarifications", required=False)
			
			self.logger.info("LLMResponse object created successfully")
			
		except Exception as e:
			self.logger.error(f"Error creating LLMResponse: {str(e)}")
			raise
	
	def _extract_field(self, json_data, field_name, field_description, required=True):
		"""Extract and validate a field from JSON data"""
		if field_name not in json_data:
			if required:
				self.logger.error(f"Missing required field '{field_name}' ({field_description})")
				raise KeyError(f"Missing required field: {field_name}")
			else:
				self.logger.debug(f"Optional field '{field_name}' not found, using None")
				return None
		
		value = json_data[field_name]
		
		# Validate non-null for required fields
		if required and (value is None or (isinstance(value, str) and value.strip() == "")):
			self.logger.error(f"Required field '{field_name}' is null or empty")
			raise ValueError(f"Required field '{field_name}' cannot be null or empty")
		
		self.logger.debug(f"Extracted {field_description}: {len(str(value))} characters")
		return value
