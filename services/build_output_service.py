import logging
from datetime import datetime

from DTO.Requests.output_request import OutputRequest


class BuildOutputService:
	def __init__(self):
		self.logger = logging.getLogger(__name__)
	
	def store_and_return_path(self, request: OutputRequest):
		self.logger.info("[BUILD-OUTPUT-SERVICE] Starting to store output files")
		
		context = request.context
		technical_todo = request.technical_todo
		clarifications = request.clarifications
		
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Context length: {len(context)} chars")
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Technical todo length: {len(technical_todo)} chars")
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Clarifications: {'Yes' if clarifications else 'No'}")

		date = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
		folder_path = "output/" + f"{date.replace(' ', '_').replace(':', '-')}"
		
		import os
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
			self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Created output directory: {folder_path}")
		
		context_file = os.path.join(folder_path, "context.md")
		with open(context_file, "w") as f:
			f.write(context)
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Wrote context to {context_file}")
		
		todo_file = os.path.join(folder_path, "todo.md")
		with open(todo_file, "w") as f:
			f.write(technical_todo)
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Wrote todo to {todo_file}")
		
		clarifications_file = os.path.join(folder_path, "clarifications.md")
		with open(clarifications_file, "w") as f:
			f.write(clarifications if clarifications else "Aucune clarification requise.")
		self.logger.debug(f"[BUILD-OUTPUT-SERVICE] Wrote clarifications to {clarifications_file}")

		self.logger.info(f"[BUILD-OUTPUT-SERVICE] Successfully stored all files in {folder_path}")
		return folder_path
