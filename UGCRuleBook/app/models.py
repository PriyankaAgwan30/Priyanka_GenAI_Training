from dataclasses import dataclass


@dataclass
class Record:
    rule_title: str
    regulation_or_circular: str
    year: int
    student_right: str
    where_to_complain: str
    source_url: str