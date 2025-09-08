import os
from openai import OpenAI, Stream
from openai.types.responses import Response, ResponseAudioDeltaEvent, ResponseAudioDoneEvent, \
	ResponseAudioTranscriptDeltaEvent, ResponseAudioTranscriptDoneEvent, ResponseCodeInterpreterCallCodeDeltaEvent, \
	ResponseCodeInterpreterCallCodeDoneEvent, ResponseCodeInterpreterCallCompletedEvent, \
	ResponseCodeInterpreterCallInProgressEvent, ResponseCodeInterpreterCallInterpretingEvent, ResponseCompletedEvent, \
	ResponseContentPartAddedEvent, ResponseContentPartDoneEvent, ResponseCreatedEvent, ResponseErrorEvent, \
	ResponseFileSearchCallCompletedEvent, ResponseFileSearchCallInProgressEvent, ResponseFileSearchCallSearchingEvent, \
	ResponseFunctionCallArgumentsDeltaEvent, ResponseFunctionCallArgumentsDoneEvent, ResponseInProgressEvent, \
	ResponseFailedEvent, ResponseIncompleteEvent, ResponseOutputItemAddedEvent, ResponseOutputItemDoneEvent, \
	ResponseReasoningSummaryPartAddedEvent, ResponseReasoningSummaryPartDoneEvent, \
	ResponseReasoningSummaryTextDeltaEvent, ResponseReasoningSummaryTextDoneEvent, ResponseReasoningTextDeltaEvent, \
	ResponseReasoningTextDoneEvent, ResponseRefusalDeltaEvent, ResponseRefusalDoneEvent, ResponseTextDeltaEvent, \
	ResponseTextDoneEvent, ResponseWebSearchCallCompletedEvent, ResponseWebSearchCallInProgressEvent, \
	ResponseWebSearchCallSearchingEvent, ResponseImageGenCallCompletedEvent, ResponseImageGenCallGeneratingEvent, \
	ResponseImageGenCallInProgressEvent, ResponseImageGenCallPartialImageEvent, ResponseMcpCallArgumentsDeltaEvent, \
	ResponseMcpCallArgumentsDoneEvent, ResponseMcpCallCompletedEvent, ResponseMcpCallFailedEvent, \
	ResponseMcpCallInProgressEvent, ResponseMcpListToolsCompletedEvent, ResponseMcpListToolsFailedEvent, \
	ResponseMcpListToolsInProgressEvent, ResponseOutputTextAnnotationAddedEvent, ResponseQueuedEvent, \
	ResponseCustomToolCallInputDeltaEvent, ResponseCustomToolCallInputDoneEvent

from DTO.Responses.open_ai_response import OpenAiResponse
from prompts.prompts import Prompt
from DTO.Requests.todo_list_request import TodoListRequest


class OpenAiController:
	def __init__(self):
		self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

	def transcript_to_todo(self, transcript):
		return self.client.responses.create(model="gpt-4o", instructions="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists.", input=Prompt.transcript_to_todo_prompt(transcript))

	def transcript_to_technical_todo(self, Request: TodoListRequest) -> OpenAiResponse:
		return OpenAiResponse(self.client.responses.create(model="gpt-4o", instructions="You are a lead full-stack developer that derives detailed technical to-do lists from meeting transcripts while respecting the actual project structure and the stack detected in the AST.", input=Prompt.transcript_to_technical_todo_prompt(Request)))

	def test(self):
		return OpenAiResponse(self.client.responses.create(model="gpt-4o", instructions="You are a helpful assistant that summarizes meeting transcripts into actionable to-do lists.", input="Fais moi une todo list pour faire un gateau au chocolat"))
