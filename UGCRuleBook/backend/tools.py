from datetime import datetime


def fee_refund_calculator(
    fee_paid,
    admission_year,
    withdrawal_date,
    policy_type,
    last_date_of_admission=None,
    full_refund_until=None,
    max_deduction_until=None,
    max_deduction=1000
):
    if fee_paid <= 0:
        raise ValueError("Fee paid must be greater than zero.")

    if max_deduction < 0:
        raise ValueError("Maximum deduction cannot be negative.")

    if not isinstance(admission_year, int):
        raise TypeError("Admission year must be an integer.")
    
    def parse_date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValueError("Dates must use YYYY-MM-DD format.")

    withdrawal = parse_date(withdrawal_date)

    if policy_type == "calendar_deadline":

        if not full_refund_until or not max_deduction_until:
            raise ValueError("Both refund deadlines are required.")

        full_date = parse_date(full_refund_until)
        deduction_date = parse_date(max_deduction_until)

        if full_date > deduction_date:
            raise ValueError("Invalid refund deadline order.")

        if withdrawal <= full_date:
            refund = fee_paid
            clause = "Full refund within the supplied deadline."

        elif withdrawal <= deduction_date:
            refund = max(0, fee_paid - max_deduction)
            clause = (
                f"Refund with maximum deduction of Rs. {max_deduction}."
            )

        else:
            raise ValueError(
                "No verified refund rule configured for this date."
            )

    elif policy_type == "five_tier_2018":

        if not last_date_of_admission:
            raise ValueError("Last date of admission is required.")

        last_date = parse_date(last_date_of_admission)
        days = (withdrawal - last_date).days

        if days <= -15:
            percentage = 100
        elif days < 0:
            percentage = 90
        elif days <= 15:
            percentage = 80
        elif days <= 30:
            percentage = 50
        else:
            percentage = 0

        refund = fee_paid * percentage / 100

        clause = (
            f"2018 five-tier table: {percentage}% refund. "
            "Processing-charge treatment must be checked separately."
        )

    else:
        raise ValueError("Unsupported policy type.")

    return {
        "fee_paid": fee_paid,
        "admission_year": admission_year,
        "withdrawal_date": withdrawal_date,
        "policy_used": policy_type,
        "clause_used": clause,
        "refund_due": round(refund, 2),
        "deduction": round(fee_paid - refund, 2)
    }