from datetime import datetime

from DTO.Requests.output_request import OutputRequest


class BuildOutputService:
	def store_and_return_path(self, request: OutputRequest):
		context = request.context
		technical_todo = request.technical_todo
		clarifications = request.clarifications

		date = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
		folder_path = "output/" + f"{date.replace(' ', '_').replace(':', '-')}"
		import os
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
		with open(os.path.join(folder_path, "context.md"), "w") as f:
			f.write(context)
		with open(os.path.join(folder_path, "todo.md"), "w") as f:
			f.write(technical_todo)
		with open(os.path.join(folder_path, "clarifications.md"), "w") as f:
			f.write(clarifications if clarifications else "Aucune clarification requise.")

		return folder_path
