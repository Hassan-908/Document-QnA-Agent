from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.agent import agent


router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


def extract_tools_used(messages):
    tools_used = []

    for message in messages:

        # ToolMessage
        if getattr(message, "type", None) == "tool":
            name = getattr(message, "name", None)

            if name and name not in tools_used:
                tools_used.append(name)

        # AIMessage containing tool calls
        tool_calls = getattr(message, "tool_calls", None)

        if tool_calls:
            for call in tool_calls:
                name = call.get("name")

                if name and name not in tools_used:
                    tools_used.append(name)

    return tools_used


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            },
            config={
                "recursion_limit": 10
            }
        )
        print("\n===== AGENT TRACE =====")

        for message in result.get("messages", []):

            print(
                "TYPE:",
                getattr(message, "type", None)
            )

            print(
                "CONTENT:",
                getattr(message, "content", None)
            )

            tool_calls = getattr(
                message,
                "tool_calls",
                None
            )

            if tool_calls:
                print(
                    "TOOL CALLS:",
                    tool_calls
                )

            print("-----------------------")

        messages = result.get("messages", [])

        if not messages:
            raise HTTPException(
                status_code=500,
                detail="Agent returned no messages."
            )

        final_message = messages[-1]

        answer = getattr(
            final_message,
            "content",
            str(final_message),
        )

        tools_used = extract_tools_used(messages)

        return {
            "question": question,
            "answer": answer,
            "tools_used": tools_used,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}"
        )