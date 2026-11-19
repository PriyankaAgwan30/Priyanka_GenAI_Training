from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    question: str
    fee_paid: float | None
    admission_year: int | None
    withdrawal_date: str | None
    policy_type: str | None
    last_date_of_admission: str | None
    full_refund_until: str | None
    max_deduction_until: str | None
    tool_used: str | None
    result: Any | None
    approval_required: bool
    approved: bool | None
    conversation_history: list


def route_question(state: AgentState):
    question = state["question"].lower()

    fee_keywords = [
        "fee refund",
        "refund my fee",
        "refund fees",
        "how much refund",
        "money back"
    ]

    if any(keyword in question for keyword in fee_keywords):
        return "fee_refund"

    return "rag_search"

from backend.rag import answer_question


def rag_search_node(state: AgentState):
    print("LangGraph: Searching UGC documents...")

    history = state.get("conversation_history", [])
    question = state["question"].lower()

    if "previous question" in question:

        if history:
            previous_question = history[-1]["question"]

            result = {
                "answer": f"Your previous question was: {previous_question}",
                "citations": []
            }
        else:
            result = {
                "answer": "There is no previous question in this conversation.",
                "citations": []
            }

    else:
        result = answer_question(
            state["question"],
            conversation_history=history
        )

    return {
        "tool_used": "rag_search",
        "result": result
    }


from backend.agent_loop import fee_refund_tool


def fee_refund_node(state: AgentState):
    print("LangGraph: Calling fee refund calculator...")

    result = fee_refund_tool(
        fee_paid=state["fee_paid"],
        admission_year=state["admission_year"],
        withdrawal_date=state["withdrawal_date"],
        policy_type=state["policy_type"],
        last_date_of_admission=state.get("last_date_of_admission"),
        full_refund_until=state.get("full_refund_until"),
        max_deduction_until=state.get("max_deduction_until")
    )

    return {
        "tool_used": "fee_refund_calculator",
        "result": result
    }


def approval_node(state: AgentState):
    print("LangGraph: Checking approval...")

    if state["approval_required"] and state["approved"] is not True:
        return {
            "result": "Approval is required before proceeding.",
            "approved": False
        }

    return {
        "approved": True
    }


def memory_node(state: AgentState):
    print("LangGraph: Saving conversation memory...")

    history = list(state.get("conversation_history", []))

    history.append({
        "question": state["question"],
        "tool_used": state["tool_used"],
        "result": state["result"]
    })

    return {
        "conversation_history": history
    }

def route_after_approval(state: AgentState):
    if state["approved"] is True:
        return "fee_refund"

    return "memory"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("rag_search", rag_search_node)
    graph.add_node("fee_refund", fee_refund_node)
    graph.add_node("approval", approval_node)
    graph.add_node("memory", memory_node)

    graph.add_conditional_edges(
        START,
        route_question,
        {
            "rag_search": "rag_search",
            "fee_refund": "approval"
        }
    )

    graph.add_edge("rag_search", "memory")

    graph.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "fee_refund": "fee_refund",
            "memory": "memory"
        }
    )

    graph.add_edge("fee_refund", "memory")
    graph.add_edge("memory", END)

    memory = MemorySaver()

    return graph.compile(checkpointer=memory)

app_graph = build_graph()

def run_graph(
    question,
    fee_paid=None,
    admission_year=None,
    withdrawal_date=None,
    policy_type=None,
    last_date_of_admission=None,
    full_refund_until=None,
    max_deduction_until=None,
    approval_required=False,
    approved=None,
    thread_id="default"
):
    graph = app_graph

    initial_state = {
        "question": question,
        "fee_paid": fee_paid,
        "admission_year": admission_year,
        "withdrawal_date": withdrawal_date,
        "policy_type": policy_type,
        "last_date_of_admission": last_date_of_admission,
        "full_refund_until": full_refund_until,
        "max_deduction_until": max_deduction_until,
        "tool_used": None,
        "result": None,
        "approval_required": approval_required,
        "approved": approved
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return graph.invoke(initial_state, config=config)