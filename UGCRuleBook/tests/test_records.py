from backend.records import count_by, get_by_id, load_records, search


def test_load_records_returns_records():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) == 20


def test_search_finds_matching_keyword():
    records = load_records()
    result = search(records, "ragging")
    assert len(result) > 0


def test_search_is_case_insensitive():
    records = load_records()
    result = search(records, "RAGGING")
    assert len(result) > 0


def test_search_returns_empty_for_unknown_keyword():
    records = load_records()
    result = search(records, "xyznotfound")
    assert result == []


def test_count_by_year():
    records = load_records()
    result = count_by(records, "year")
    assert result[2023] == 10


def test_get_by_id_returns_correct_record():
    records = load_records()
    result = get_by_id(records, 1)
    assert result == records[0]
    assert result["rule_title"] == "Student Grievance Regulations 2023"


def test_get_by_id_invalid_returns_none():
    records = load_records()
    assert get_by_id(records, 0) is None
    assert get_by_id(records, 21) is None