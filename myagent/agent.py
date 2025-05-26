from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import LongRunningFunctionTool

from google.adk.tools import FunctionTool, ToolContext

from pprint import pprint
import httpx

async def ask_human(tool_context: ToolContext, question: str) -> str:
    # Extract session info
    session_id = tool_context._invocation_context.session.id
    user_id = tool_context._invocation_context.user_id
    app_name = tool_context._invocation_context.app_name
    # Prepare payload
    payload = {
        "session_info": {
            "user_id": user_id,
            "appname": app_name,
            "session_id": session_id
        },
        "question_text": question,
        "persona": "developer"
    }
    # Send POST request to handoff endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://hitl.codeshare.live/handoff/",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload
        )
    # Return JSON response or fallback to text
    try:
        return response.json()
    except ValueError:
        return response.text


root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    description="""
        You are a helpful agent you ask the human whatever question user asks you to ask the human.
        You have a tool named ask_human that you can use to ask the human a question.
        This is a human in the loop tool which will send a question to the human and wait for their response.
    """,
    tools=[
        LongRunningFunctionTool(ask_human)
        # MCPToolset(
        #     connection_params=SseServerParams(url="http://localhost:8900/mcp", headers={'Session-Id': example_session.id}),
        # )
    ],
)
