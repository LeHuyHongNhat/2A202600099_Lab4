import time
import json
import logging
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from tools import search_flights, search_hotels, calculate_budget, format_response
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
logger = logging.getLogger("travelbuddy")

_turn = 0

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget, format_response]
llm = ChatOpenAI(model="gpt-5-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        for tc in response.tool_calls:
            args_str = json.dumps(tc["args"], ensure_ascii=False)
            print(f"  -> Goi tool: {tc['name']}")
            logger.info("TOOL_CALL  name=%s  args=%s", tc["name"], args_str)
    else:
        logger.info("DIRECT_RESPONSE  (no tool call)")

    return {"messages": [response]}

# 5. Xây dựng Graph
def after_tools_condition(state: AgentState) -> str:
    """Sau khi tools chạy xong: nếu format_response vừa được gọi thì kết thúc,
    ngược lại quay lại agent để tiếp tục."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            if any(tc["name"] == "format_response" for tc in msg.tool_calls):
                return END
            return "agent"
    return "agent"

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_conditional_edges("tools", after_tools_condition)

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("TravelBuddy - Tro ly Du lich Thong minh")
    print("Go 'quit' de thoat\n")

    while True:
        user_input = input("Ban: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Tam biet!")
            break

        _turn += 1
        t_start = time.time()
        logger.info("--- TURN #%d ---", _turn)
        logger.info("USER  %s", user_input)

        print("TravelBuddy dang suy nghi, doi chut nhe...")
        result = graph.invoke({"messages": [("human", user_input)]})

        tool_calls_total = 0
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                tool_calls_total += len(msg.tool_calls)
            if isinstance(msg, ToolMessage):
                logger.info("TOOL_RESULT  name=%s  content=%s", msg.tool_call_id, msg.content)

        elapsed = time.time() - t_start
        final_content = result["messages"][-1].content
        logger.info("ASSISTANT  %s", final_content)
        logger.info("TURN_DONE  elapsed=%.1fs  tool_calls=%d", elapsed, tool_calls_total)

        print(f"\nTravelBuddy: {final_content.replace('#', '').replace('*', '')}\n")