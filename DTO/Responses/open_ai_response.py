import json


class OpenAiResponse:
	def __init__(self, response):
		_response_json = json.loads(response.choices[0].message.content)
		print(_response_json)
		self.context = _response_json["contexte"]
		self.technical_todo = _response_json["technical_todolist"]
		self.clarifications = _response_json["clarifications_requises"]

	def get_name(self) -> str:
		return self.name

	def get_technical_todo(self) -> str:
		return self.technical_todo

	def get_clarifications(self) -> str:
		return self.clarifications

	def get_context(self) -> str:
		return self.context
