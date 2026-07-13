from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from state import BookingState

from agents import (
    triage_agent,
    booking_specialist,
    general_agent
)

def route_intent(state):
    return state["intent"]
graph_builder = StateGraph(BookingState)

graph_builder.add_node("triage", triage_agent)
graph_builder.add_node("booking", booking_specialist)
graph_builder.add_node("general", general_agent)

graph_builder.add_edge(START, "triage")
graph_builder.add_conditional_edges(
    "triage",
    route_intent,
    {
        "book": "booking",
        "availability": "booking",
        "booking_details": "booking",
        "general": "general"
    }
)

graph_builder.add_edge("general", END)
graph_builder.add_edge("booking", END)

from langgraph.checkpoint.sqlite import SqliteSaver

memory_context = SqliteSaver.from_conn_string("conversation_memory.db")
memory = memory_context.__enter__()

graph = graph_builder.compile(
    checkpointer=memory
)