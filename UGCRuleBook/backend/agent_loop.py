
from backend.rag import answer_question
from backend.tools import fee_refund_calculator


def rag_search_tool(question):
    """
    Search UGC documents and return an evidence-based answer.
    """
    if not question or not question.strip():
        return {
            "answer": (
                "Please enter a question about a student right, and I'll "
                "look it up in the UGC regulations."
            ),
            "citations": []
        }

    return answer_question(question)



def fee_refund_tool(
    fee_paid,
    admission_year,
    withdrawal_date,
    policy_type,
    last_date_of_admission=None,
    full_refund_until=None,
    max_deduction_until=None,
    max_deduction=1000
):
    """
    Calculate the student's fee refund using the selected policy.
    """

    return fee_refund_calculator(
        fee_paid=fee_paid,
        admission_year=admission_year,
        withdrawal_date=withdrawal_date,
        policy_type=policy_type,
        last_date_of_admission=last_date_of_admission,
        full_refund_until=full_refund_until,
        max_deduction_until=max_deduction_until,
        max_deduction=max_deduction
    )





def run_agent(
    question,
    fee_paid=None,
    admission_year=None,
    withdrawal_date=None,
    policy_type=None,
    last_date_of_admission=None,
    full_refund_until=None,
    max_deduction_until=None
):
    """
    Hand-written agent loop that selects the appropriate tool.
    """

    if not question or not question.strip():
        return {
            "tool_used": None,
            "result": "Please enter a question."
        }

    question_lower = question.lower()

    fee_keywords = [
        "fee refund",
        "refund my fee",
        "refund fees",
        "how much refund",
        "money back"
    ]

    if any(keyword in question_lower for keyword in fee_keywords):

        if (
            fee_paid is None
            or admission_year is None
            or withdrawal_date is None
            or policy_type is None
        ):
            return {
                "tool_used": None,
                "result": (
                    "Please provide fee paid, admission year, "
                    "withdrawal date, and applicable refund policy."
                )
            }

        print("Agent decision: Calling fee refund calculator...")

        result = fee_refund_tool(
            fee_paid=fee_paid,
            admission_year=admission_year,
            withdrawal_date=withdrawal_date,
            policy_type=policy_type,
            last_date_of_admission=last_date_of_admission,
            full_refund_until=full_refund_until,
            max_deduction_until=max_deduction_until
        )

        return {
            "tool_used": "fee_refund_calculator",
            "result": result
        }

    print("Agent decision: Searching UGC documents...")
    
    result = rag_search_tool(question)

    return {
        "tool_used": "rag_search",
        "result": result
    }

