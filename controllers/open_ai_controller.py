import os
from openai import OpenAI
from DTO.Responses.open_ai_response import OpenAiResponse
from prompts.prompts import Prompt
from DTO.Requests.todo_list_request import TodoListRequest
from utils.json_schemas import JsonSchema


class OpenAiController:
	def __init__(self):
		self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

	def transcript_to_todo(self, transcript):
		return self.client.responses.create(model="gpt-4o", instructions="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists.", input=Prompt.transcript_to_todo_prompt(transcript))

	def transcript_to_technical_todo(self, Request: TodoListRequest) -> OpenAiResponse:
		return OpenAiResponse(self.client.chat.completions.create(model="gpt-5-mini", messages=[{"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists."}, {"role": "user", "content": Prompt.transcript_to_technical_todo_prompt(Request)}], response_format={"type": "json_schema", "json_schema": JsonSchema.technical_todo_schema()}))

	def test(self):
		return OpenAiResponse(self.client.responses.create(model="gpt-4o", instructions="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists.", input="Fais moi une todo list pour faire un gateau au chocolat"))
