"""
Simplified prompts for smaller LLMs like gemma:2b
"""
from DTO.Requests.todo_list_request import TodoListRequest


class SimplePrompt:
    @staticmethod
    def transcript_to_technical_todo_prompt(Request: TodoListRequest):
        """Simplified prompt that gemma:2b can handle"""
        
        return f"""You are a developer creating a technical TODO list from meeting notes.

PROJECT STRUCTURE:
{Request.parsed_project}

MEETING NOTES:
{Request.transcript}

Create a simple JSON response with these 3 fields:

1. "contexte": A 2-3 sentence summary of what needs to be done
2. "technical_todolist": A bullet list of specific technical tasks (use - for bullets)
3. "clarifications_requises": Questions you have (or "None" if clear)

Example format:
{{
  "contexte": "This project needs form validation and homepage updates.",
  "technical_todolist": "- Add email validation to contact form\\n- Update homepage logo\\n- Test form submission",
  "clarifications_requises": "None"
}}

Respond ONLY with valid JSON. No markdown code blocks, no extra text."""

