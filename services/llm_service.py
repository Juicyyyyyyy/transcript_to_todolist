import os
import json
import logging
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.llms import ChatMessage
from DTO.Responses.llm_response import LLMResponse
from prompts.prompts_structured import StructuredPrompt  # Using structured prompts with categories
from DTO.Requests.todo_list_request import TodoListRequest
from utils.json_schemas import JsonSchema


class LLMService:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.logger.info("Initializing LLM Service with LlamaIndex")
		
		try:
			self.llm = OpenAILike(
				model="gemma:2b",
				api_base="http://localhost:11434/v1",
				api_key="ollama",
				context_window=128000,
				is_chat_model=True,
				is_function_calling_model=False,
				request_timeout=600  # 10 minutes for complex JSON generation
			)
			self.logger.info("LLM client initialized successfully with model: gemma:2b")
		except Exception as e:
			self.logger.error(f"Failed to initialize LLM client: {str(e)}")
			raise

	def transcript_to_technical_todo(self, Request: TodoListRequest) -> LLMResponse:
		self.logger.info("[LLM-SERVICE] Starting transcript to technical todo conversion")
		self.logger.debug(f"[LLM-SERVICE] Transcript length: {len(Request.transcript)} chars")
		self.logger.debug(f"[LLM-SERVICE] Parsed project length: {len(Request.parsed_project)} chars")
		
		try:
			# Generate the prompt (using structured version with categories)
			prompt_content = StructuredPrompt.transcript_to_technical_todo_prompt(Request)
			self.logger.info(f"[LLM-SERVICE] Generated prompt, total length: {len(prompt_content)} characters")
			self.logger.debug(f"[LLM-SERVICE] Prompt preview (first 500 chars): {prompt_content[:500]}...")
			
			# Prepare JSON schema
			schema = JsonSchema.technical_todo_schema()
			schema_json = json.dumps(schema, indent=2)
			self.logger.debug(f"[LLM-SERVICE] JSON schema length: {len(schema_json)} chars")
			
			# Prepare messages with JSON schema enforcement
			system_message = "You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists. You MUST respond with valid JSON that strictly follows the provided schema."
			user_message = f"{prompt_content}\n\nIMPORTANT: You must respond with valid JSON that follows this exact schema:\n{schema_json}"
			
			self.logger.debug(f"[LLM-SERVICE] System message length: {len(system_message)} chars")
			self.logger.debug(f"[LLM-SERVICE] User message length: {len(user_message)} chars")
			
			messages = [
				ChatMessage(role="system", content=system_message),
				ChatMessage(role="user", content=user_message)
			]
			
			self.logger.info("[LLM-SERVICE] Sending request to LLM API...")
			self.logger.debug(f"[LLM-SERVICE] LLM config - model: gemma3:latest, timeout: 300s, context_window: 128000")
			
			response = self.llm.chat(messages)
			
			self.logger.info("[LLM-SERVICE] ✓ Received response from LLM API")
			
			# Log response details
			if hasattr(response, 'message') and hasattr(response.message, 'content'):
				content_length = len(response.message.content)
				self.logger.info(f"[LLM-SERVICE] Response content length: {content_length} characters")
				self.logger.debug(f"[LLM-SERVICE] Response preview (first 500 chars): {response.message.content[:500]}...")
			else:
				self.logger.warning("[LLM-SERVICE] Response format unexpected, attempting to extract content")
				self.logger.debug(f"[LLM-SERVICE] Response type: {type(response)}")
			
			# Create LLMResponse with validation
			self.logger.debug("[LLM-SERVICE] Creating LLMResponse object...")
			llm_response = LLMResponse(response)
			self.logger.info("[LLM-SERVICE] ✓ Successfully created LLMResponse object")
			
			# Validate the response against the schema
			self.logger.debug("[LLM-SERVICE] Validating response schema...")
			self._validate_response_schema(llm_response)
			
			self.logger.info("[LLM-SERVICE] ✓✓ Transcript to technical todo conversion completed successfully")
			self.logger.info(f"[LLM-SERVICE] Result summary - Context: {len(llm_response.context)} chars, Todo: {len(llm_response.technical_todo)} chars, Clarifications: {len(llm_response.clarifications) if llm_response.clarifications else 0} chars")
			return llm_response
			
		except json.JSONDecodeError as e:
			self.logger.error(f"[LLM-SERVICE] ✗ JSON parsing error: {str(e)}", exc_info=True)
			self.logger.error("[LLM-SERVICE] LLM response was not valid JSON")
			raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
		except KeyError as e:
			self.logger.error(f"[LLM-SERVICE] ✗ Missing required field in response: {str(e)}", exc_info=True)
			raise ValueError(f"Response missing required field: {str(e)}")
		except Exception as e:
			self.logger.error(f"[LLM-SERVICE] ✗ LLM API Error: {str(e)}", exc_info=True)
			# Log more details about the error
			if hasattr(e, 'response'):
				self.logger.error(f"[LLM-SERVICE] Error response: {e.response}")
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
