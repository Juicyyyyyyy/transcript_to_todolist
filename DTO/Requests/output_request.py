class OutputRequest:
	def __init__(self, context: str, technical_todo: str, clarifications: str):
		self.context = context
		self.technical_todo = technical_todo
		self.clarifications = clarifications
