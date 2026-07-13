from typing import Annotated, Optional
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class BookingState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    intent: Optional[str]

    date: Optional[str]

    time: Optional[str]

    email: Optional[str]

    available_slots: Optional[list[str]]

    booking_status: Optional[str]

    response: Optional[str]