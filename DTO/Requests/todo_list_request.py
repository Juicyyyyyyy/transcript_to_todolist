class TodoListRequest:
	def __init__(self, parsed_project: str, transcript: str):
		self.parsed_project: str = parsed_project
		self.transcript: str = transcript

	def get_parsed_project(self) -> str:
		return self.parsed_project

	def get_transcript(self) -> str:
		return self.transcript
