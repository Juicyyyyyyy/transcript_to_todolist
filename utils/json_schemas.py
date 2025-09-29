class JsonSchema:
	@staticmethod
	def technical_todo_schema():
		return {
			"name": "technical_todo_response",
			"strict": True,
			"schema": {
				"type": "object",
				"additionalProperties": False,
				"properties": {
					"contexte": {
						"type": "string",
						"description": "Contexte et courte description de la réunion sous forme non technique (Markdown).",
					},
					"technical_todolist": {
						"type": "string",
						"minLength": 1,
						"description": "Liste technique (Markdown)."
					},
					"clarifications_requises": {
						"type": "string",
						"description": "Questions/points à clarifier (Markdown), facultatif.",
						"nullable": True
					}
				},
				"required": ["contexte", "technical_todolist", "clarifications_requises"]
			}
		}
