import json


class OpenAiResponse:
	def __init__(self, response):
		_response_json = json.loads(response.choices[0].message.content)
		self.context = _response_json["contexte"]
		self.technical_todo = _response_json["technical_todolist"]
		self.clarifications = _response_json["clarifications_requises"]
