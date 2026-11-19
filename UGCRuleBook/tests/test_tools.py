import pytest

from backend.tools import fee_refund_calculator


def test_full_refund_before_deadline():
    result = fee_refund_calculator(
        fee_paid=50000,
        admission_year=2023,
        withdrawal_date="2023-09-10",
        policy_type="calendar_deadline",
        full_refund_until="2023-09-15",
        max_deduction_until="2023-10-31"
    )

    assert result["refund_due"] == 50000
    assert result["deduction"] == 0


def test_refund_with_deduction():
    result = fee_refund_calculator(
        fee_paid=50000,
        admission_year=2023,
        withdrawal_date="2023-10-10",
        policy_type="calendar_deadline",
        full_refund_until="2023-09-15",
        max_deduction_until="2023-10-31",
        max_deduction=1000
    )

    assert result["refund_due"] == 49000
    assert result["deduction"] == 1000


def test_five_tier_policy_80_percent_refund():
    result = fee_refund_calculator(
        fee_paid=50000,
        admission_year=2018,
        withdrawal_date="2023-08-01",
        policy_type="five_tier_2018",
        last_date_of_admission="2023-07-31"
    )

    assert result["refund_due"] == 40000
    assert result["deduction"] == 10000


def test_invalid_fee_raises_error():
    with pytest.raises(ValueError, match="Fee paid must be greater than zero"):
        fee_refund_calculator(
            fee_paid=0,
            admission_year=2023,
            withdrawal_date="2023-09-10",
            policy_type="calendar_deadline",
            full_refund_until="2023-09-15",
            max_deduction_until="2023-10-31"
        )


def test_invalid_date_raises_error():
    with pytest.raises(ValueError, match="Dates must use YYYY-MM-DD format"):
        fee_refund_calculator(
            fee_paid=50000,
            admission_year=2023,
            withdrawal_date="invalid-date",
            policy_type="calendar_deadline",
            full_refund_until="2023-09-15",
            max_deduction_until="2023-10-31"
        )


def test_unsupported_policy_raises_error():
    with pytest.raises(ValueError, match="Unsupported policy type"):
        fee_refund_calculator(
            fee_paid=50000,
            admission_year=2023,
            withdrawal_date="2023-09-10",
            policy_type="unknown_policy"
        )