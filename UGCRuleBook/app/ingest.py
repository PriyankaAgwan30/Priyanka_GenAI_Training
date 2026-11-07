
import json
import os
from dataclasses import asdict

from pypdf import PdfReader
from app.models import Record


pdf_files = [
    "data/raw/grievance_2023.pdf",
    "data/raw/grievance_2019.pdf",
    "data/raw/ragging_2013.pdf"
]

for file_path in pdf_files:
    try:
        reader = PdfReader(file_path)
        print(file_path, "- Pages:", len(reader.pages))

    except Exception as error:
        print("Error reading file:", error)


raw_records = [
    {
        "rule_title": "False Information in Prospectus",
        "regulation_or_circular": "UGC Grievance Regulations",
        "year": 2023,
        "student_right": "Students can complain about false or misleading information in the prospectus.",
        "where_to_complain": "Students' Grievance Redressal Committee",
        "source_url": "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"
    },
    {
        "rule_title": "Retention of Student Documents",
        "regulation_or_circular": "UGC Grievance Regulations",
        "year": 2023,
        "student_right": "Students can complain if their certificates or documents are improperly retained.",
        "where_to_complain": "Students' Grievance Redressal Committee",
        "source_url": "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"
    },
    {
        "rule_title": "Delay in Fee Refund",
        "regulation_or_circular": "UGC Grievance Regulations",
        "year": 2023,
        "student_right": "Students can complain about delays in eligible fee refunds.",
        "where_to_complain": "Students' Grievance Redressal Committee",
        "source_url": "https://www.ugc.gov.in/pdfnews/4675881_Regulation.pdf"
    }
]


records = []

for row in raw_records:
    try:
        record = Record(**row)
        records.append(asdict(record))

    except (TypeError, KeyError) as error:
        print("Invalid record:", error)


os.makedirs("data", exist_ok=True)

with open("data/records.json", "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4, ensure_ascii=False)

print("\nRecords saved successfully!")
print("Total records:", len(records))
