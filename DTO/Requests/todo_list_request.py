class TodoListRequest:
	def __init__(self, parsed_project: str, transcript: str):
		self.parsed_project: str = parsed_project
		self.transcript: str = transcript
