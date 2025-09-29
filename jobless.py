import argparse
from datetime import datetime

from DTO.Requests.todo_list_request import TodoListRequest
from controllers.open_ai_controller import OpenAiController

from docx import Document
from dotenv import load_dotenv

load_dotenv()


def read_docx(path: str) -> str:
	doc = Document(path)
	return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def main():
	parser = argparse.ArgumentParser(description="My Python CLI tool")

	parser.add_argument("transcript_path", help="Path to transcript")
	parser.add_argument("project_path", nargs="?", default=".", help="Path to project (default: current directory)")
	parser.add_argument("-o", "--output", type=str, help="Path to the output folder")
	# parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

	args = parser.parse_args()

	# test
	# controller = OpenAiController()
	# response = controller.test()
	# print(response)
	# print(response.get_output_text())

	transcript = read_docx(args.transcript_path)
	controller = OpenAiController()
	request = TodoListRequest(parsed_project=args.project_path, transcript=transcript)
	response = controller.transcript_to_technical_todo(request)
	date = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
	context = response.get_context()
	technical_todo = response.get_technical_todo()
	clarifications = response.get_clarifications()

	# Create a folder of format name-date, inside this folder create a todo.md file and a clarifications.md file
	folder_name = "output/" + f"{date.replace(' ', '_').replace(':', '-')}"
	folder_path = args.output if args.output else folder_name
	import os
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
	with open(os.path.join(folder_path, "context.md"), "w") as f:
		f.write(context)
	with open(os.path.join(folder_path, "todo.md"), "w") as f:
		f.write(technical_todo)
	with open(os.path.join(folder_path, "clarifications.md"), "w") as f:
		f.write(clarifications if clarifications else "Aucune clarification requise.")


if __name__ == "__main__":
	main()
