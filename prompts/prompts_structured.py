"""
Structured prompts that generate detailed technical TODOs with categories
Optimized for gemma:2b while maintaining detail
"""
from DTO.Requests.todo_list_request import TodoListRequest


class StructuredPrompt:
    @staticmethod
    def transcript_to_technical_todo_prompt(Request: TodoListRequest):
        """
        Prompt that generates structured technical TODOs with multiple categories.
        Balanced between detail and model capability.
        """
        
        return f"""You are a technical lead creating a detailed TODO list from meeting notes.

PROJECT CODE STRUCTURE:
{Request.parsed_project}

MEETING TRANSCRIPT:
{Request.transcript}

You MUST create a JSON response with EXACTLY these 3 field names:

1. "contexte" (NOT "context"): Brief summary (2-3 sentences) of what needs to be done

2. "technical_todolist" (NOT "tasks" or "todolist"): Organized technical tasks in Markdown format with sections:
   
   **Backend**
   - [ ] P1 · Task description with file paths
   - [ ] P2 · Another task
   
   **Frontend**  
   - [ ] P1 · Task description with component names
   
   **Database**
   - [ ] P0 · Migration tasks if needed
   
   **Tests**
   - [ ] P2 · Test requirements

   Priority levels: P0 (critical), P1 (high), P2 (nice-to-have)
   
   For each task:
   - Specify exact file paths from the project structure
   - Mention specific functions/classes/components to modify
   - Include endpoints or routes if relevant
   
3. "clarifications_requises" (NOT "clarifications"): Questions about unclear requirements, or "None" if everything is clear

CRITICAL: You MUST use these EXACT field names: "contexte", "technical_todolist", "clarifications_requises"

IMPORTANT RULES:
- Use the actual file paths and structure from the project code above
- Reference specific files, classes, and functions mentioned in the project structure
- Organize tasks by category (Backend, Frontend, Database, Tests)
- Add priority levels (P0, P1, P2) to each task
- Respond ONLY with valid JSON (no markdown blocks, no extra text)

Example output format:
{{
  "contexte": "This project needs form validation and homepage updates based on the meeting discussion.",
  "technical_todolist": "**Backend**\\n- [ ] P1 · Add email validation in contact.php validateEmail() function\\n- [ ] P1 · Update homepage header in index.php\\n\\n**Frontend**\\n- [ ] P2 · Update logo in style.css header section\\n\\n**Tests**\\n- [ ] P2 · Add validation tests for contact form",
  "clarifications_requises": "None"
}}

Now generate the JSON for the above project and meeting notes."""

