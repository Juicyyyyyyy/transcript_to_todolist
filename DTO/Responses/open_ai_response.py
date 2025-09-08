class OpenAiResponse:
	def __init__(self, response):
		self.output_text = response.output_text

	def get_output_text(self):
		return self.output_text
