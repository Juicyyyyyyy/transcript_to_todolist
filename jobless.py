import argparse

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
	parser.add_argument("-o", "--output", type=str, help="Path to the output")
	# parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

	args = parser.parse_args()

	# test
	controller = OpenAiController()
	response = controller.test()
	print(response)
	print(response.get_output_text())

	transcript = read_docx(args.transcript_path)
	controller = OpenAiController()
	request = TodoListRequest(parsed_project=args.project_path, transcript=transcript)
	response = controller.transcript_to_technical_todo(request)
	print(response.get_output_text())

	if args.output:
		with open(args.output, "w") as f:
			f.write(response.get_output_text())


if __name__ == "__main__":
	main()
