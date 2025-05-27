from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import LongRunningFunctionTool

from google.adk.tools import FunctionTool, ToolContext

from pprint import pprint
import httpx

async def ask_underwriter(tool_context: ToolContext, question: str) -> str:
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
        Yuor name is leo and you are a junior underwriter ai agent, given the initial analysis your job is to generate a initial report and present to the uer and also you need to ask for review from underwriter for approval of your decision. you need to show him your analysis in best possible so that he can provide the right feedback view to get the feedback from him in terms of approval, so while using the tool ask_underwriter, provide the analysis you have done so far and ask for his feedback in best possible way.
    """,
    tools=[
        LongRunningFunctionTool(ask_underwriter)
        # MCPToolset(
        #     connection_params=SseServerParams(url="http://localhost:8900/mcp", headers={'Session-Id': example_session.id}),
        # )
    ],
)
