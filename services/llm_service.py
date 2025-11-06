import os
import json
import logging
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage
from DTO.Responses.llm_response import LLMResponse
from prompts.prompts import Prompt
from DTO.Requests.todo_list_request import TodoListRequest
from utils.json_schemas import JsonSchema


class LLMService:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.info("Initializing LLM Service with LlamaIndex")
		
		try:
			self.llm = OpenAILike(
				model="gemma3:latest",
				api_base="http://localhost:11434/v1",
				api_key="ollama",
				context_window=128000,
				is_chat_model=True,
				is_function_calling_model=False,
				request_timeout=300
			)
			self.logger.info("LLM client initialized successfully with model: gemma3:latest")
		except Exception as e:
			self.logger.error(f"Failed to initialize LLM client: {str(e)}")
			raise

	def transcript_to_technical_todo(self, Request: TodoListRequest) -> LLMResponse:
		self.logger.info("Starting transcript to technical todo conversion")
		self.logger.debug(f"Request received: {Request}")
		
		try:
			# Generate the prompt
			prompt_content = Prompt.transcript_to_technical_todo_prompt(Request)
			self.logger.debug(f"Generated prompt length: {len(prompt_content)} characters")
			
			# Prepare messages with JSON schema enforcement
			messages = [
				ChatMessage(
					role="system",
					content="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists. You MUST respond with valid JSON that strictly follows the provided schema."
				),
				ChatMessage(
					role="user", 
					content=f"{prompt_content}\n\nIMPORTANT: You must respond with valid JSON that follows this exact schema:\n{json.dumps(JsonSchema.technical_todo_schema(), indent=2)}"
				)
			]
			
			self.logger.info("Sending request to LLM")
			response = self.llm.chat(messages)
			self.logger.info("Received response from LLM")
			
			# Log response details
			if hasattr(response, 'message') and hasattr(response.message, 'content'):
				content_length = len(response.message.content)
				self.logger.debug(f"Response content length: {content_length} characters")
			else:
				self.logger.warning("Response format unexpected, attempting to extract content")
			
			# Create LLMResponse with validation
			llm_response = LLMResponse(response)
			self.logger.info("Successfully created LLMResponse object")
			
			# Validate the response against the schema
			self._validate_response_schema(llm_response)
			
			self.logger.info("Transcript to technical todo conversion completed successfully")
			return llm_response
			
		except json.JSONDecodeError as e:
			self.logger.error(f"JSON parsing error: {str(e)}")
			self.logger.error("LLM response was not valid JSON")
			raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
		except KeyError as e:
			self.logger.error(f"Missing required field in response: {str(e)}")
			raise ValueError(f"Response missing required field: {str(e)}")
		except Exception as e:
			self.logger.error(f"LLM API Error: {str(e)}")
			raise

	def _validate_response_schema(self, llm_response: LLMResponse):
		"""Validate the LLM response against the required JSON schema"""
		self.logger.debug("Validating response against JSON schema")
		
		# Check required fields
		required_fields = ["contexte", "technical_todolist", "clarifications_requises"]
		response_data = {
			"contexte": llm_response.context,
			"technical_todolist": llm_response.technical_todo,
			"clarifications_requises": llm_response.clarifications
		}
		
		for field in required_fields:
			if field not in response_data or response_data[field] is None:
				self.logger.error(f"Missing required field: {field}")
				raise ValueError(f"Response missing required field: {field}")
		
		# Validate technical_todolist has minimum length
		if len(llm_response.technical_todo.strip()) < 1:
			self.logger.error("technical_todolist is empty or too short")
			raise ValueError("technical_todolist must have at least 1 character")
		
		self.logger.debug("Response validation passed")
	
	def test_api_call(self):
		self.logger.info("Testing LLM API connection")
		try:
			messages = [
				ChatMessage(
					role="system",
					content="You are a helpful assistant."
				),
				ChatMessage(
					role="user", 
					content="Hello, how are you?"
				)
			]
			self.logger.debug("Sending test message to LLM")
			response = self.llm.chat(messages)
			self.logger.info("Test API call successful")
			return response
		except Exception as e:
			self.logger.error(f"Test API call failed: {str(e)}")
			raise
