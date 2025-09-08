import os
from openai import OpenAI
from prompts.prompts import Prompt


class OpenAiRequests:
	def __init__(self):
		self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), )

	def transcript_to_todo(self, transcript):
		return self.client.responses.create(model="gpt-4o", instructions="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists.", input=Prompt.transcript_to_todo_prompt(transcript))
