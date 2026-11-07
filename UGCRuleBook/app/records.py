
from data.sample_records import records


def load_records():
    return records


def search(records, keyword):
    results = []

    for record in records:
        for value in record.values():
            if keyword.lower() in str(value).lower():
                results.append(record)
                break

    return results


def count_by(records, field):
    counts = {}

    for record in records:
        category = record[field]
        counts[category] = counts.get(category, 0) + 1

    return counts


def get_by_id(records, record_id):
    if 1 <= record_id <= len(records):
        return records[record_id - 1]

    return None
